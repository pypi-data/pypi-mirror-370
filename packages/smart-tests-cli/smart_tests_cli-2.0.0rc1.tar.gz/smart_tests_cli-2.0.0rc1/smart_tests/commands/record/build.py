import os
import re
import sys
from typing import Annotated, List

import typer
from tabulate import tabulate

from smart_tests.utils.link import CIRCLECI_KEY, GITHUB_ACTIONS_KEY, JENKINS_URL_KEY, capture_link
from smart_tests.utils.tracking import Tracking, TrackingClient

from ...utils import subprocess
from ...utils.authentication import get_org_workspace
from ...utils.launchable_client import LaunchableClient
from ...utils.typer_types import validate_datetime_with_tz, validate_key_value, validate_past_datetime
from .commit import commit

JENKINS_GIT_BRANCH_KEY = "GIT_BRANCH"
JENKINS_GIT_LOCAL_BRANCH_KEY = "GIT_LOCAL_BRANCH"
GITHUB_ACTIONS_GITHUB_HEAD_REF_KEY = "GITHUB_HEAD_REF"
GITHUB_ACTIONS_GITHUB_BASE_REF_KEY = "GITHUB_BASE_REF"
CIRCLECI_CIRCLE_BRANCH_KEY = "CIRCLE_BRANCH"
CODE_BUILD_BUILD_ID_KEY = "CODEBUILD_BUILD_ID"
CODE_BUILD_WEBHOOK_HEAD_REF_KEY = "CODEBUILD_WEBHOOK_HEAD_REF"


app = typer.Typer(name="build", help="Record build information")


@app.callback(invoke_without_command=True)
def build(
    ctx: typer.Context,
    build_name: Annotated[str, typer.Option(
        "--build",
        help="build name",
        metavar="BUILD_NAME"
    )],
    branch: Annotated[str | None, typer.Option(
        "--branch",
        help="Branch name. A branch is a set of test sessions grouped and this option value will be used for a lineage name."
    )] = None,
    repositories: Annotated[List[str], typer.Option(
        "--repo-branch-map",
        help="Set repository name and branch name when you use --no-commit-collection option. "
             "Please use the same repository name with a commit option"
    )] = [],
    source: Annotated[List[str], typer.Option(
        help="path to local Git workspace, optionally prefixed by a label. "
             "like --source path/to/ws or --source main=path/to/ws",
        metavar="REPO_NAME"
    )] = ["."],
    max_days: Annotated[int, typer.Option(
        help="the maximum number of days to collect commits retroactively"
    )] = 30,
    no_submodules: Annotated[bool, typer.Option(
        help="stop collecting information from Git Submodules"
    )] = False,
    no_commit_collection: Annotated[bool, typer.Option(
        help="do not collect commit data. "
             "This is useful if the repository is a shallow clone and the RevWalk is not "
             "possible. The commit data must be collected with a separate fully-cloned "
             "repository."
    )] = False,
    commits: Annotated[List[str], typer.Option(
        "--commit",
        help="set repository name and commit hash when you use --no-commit-collection option"
    )] = [],
    timestamp: Annotated[str | None, typer.Option(
        help="Used to overwrite the build time when importing historical data. "
             "Note: Format must be `YYYY-MM-DDThh:mm:ssTZD` or `YYYY-MM-DDThh:mm:ss` (local timezone applied)"
    )] = None,
):
    app = ctx.obj

    # Parse key-value pairs for commits
    parsed_commits = [validate_key_value(c) for c in commits]

    # Parse timestamp if provided
    parsed_timestamp = None
    if timestamp:
        parsed_timestamp = validate_past_datetime(validate_datetime_with_tz(timestamp))

    if "/" in build_name or "%2f" in build_name.lower():
        typer.echo("--build must not contain a slash and an encoded slash", err=True)
        raise typer.Exit(1)
    if "%25" in build_name:
        typer.echo("--build must not contain encoded % (%25)", err=True)
        raise typer.Exit(1)
    if not no_commit_collection and len(parsed_commits) != 0:
        typer.echo("--no-commit-collection must be specified when --commit is used", err=True)
        raise typer.Exit(1)
    if not no_commit_collection and len(repositories) != 0:
        typer.echo("--no-commit-collection must be specified when --repo-branch-map is used", err=True)
        raise typer.Exit(1)

    # Information we want to collect for each Git repository
    # The key data structure throughout the implementation of this command

    class Workspace:
        # identifier given to a Git repository to track the same repository from one 'record build' to next
        name: str
        # path to the Git workspace. Can be None if there's no local workspace present
        dir: str
        # current branch of this workspace
        branch: str | None = None
        # SHA1 commit hash that's currently checked out
        commit_hash: str

        def __init__(self, name, dir=None, commit_hash=None):
            self.name = name
            self.dir = dir
            self.commit_hash = commit_hash

        def calc_branch_name(self):
            '''
            figure out the branch using the workspace. requires `dir` and `commit_hash` to be set.
            '''

            # Jenkins
            # ref:
            # https://www.theserverside.com/blog/Coffee-Talk-Java-News-Stories-and-Opinions/Complete-Jenkins-Git-environment-variables-list-for-batch-jobs-and-shell-script-builds
            if os.environ.get(JENKINS_URL_KEY):
                self.branch = os.environ.get(JENKINS_GIT_BRANCH_KEY) or os.environ.get(JENKINS_GIT_LOCAL_BRANCH_KEY)

            # Github Actions
            # ref: https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables
            # These environment variables cannot be retrieved when a `push` event is emitted.
            # Here is a note regarding the output of `git show-ref`:
            # - Git tag is pushed during a `push` event
            #   => ed6de84bde58d51deebe90e01ddfa5fa78899b1c refs/tags/tag-name
            # - Git commit is pushed during a `push` event
            #   => ed6de84bde58d51deebe90e01ddfa5fa78899b1c refs/heads/branch/branch-name
            if os.environ.get(GITHUB_ACTIONS_KEY):
                self.branch = os.environ.get(GITHUB_ACTIONS_GITHUB_HEAD_REF_KEY) or \
                    os.environ.get(GITHUB_ACTIONS_GITHUB_BASE_REF_KEY)

            # CircleCI
            # ref: https://circleci.com/docs/variables/
            if os.environ.get(CIRCLECI_KEY):
                self.branch = os.environ.get(CIRCLECI_CIRCLE_BRANCH_KEY)
            # AWS CodeBuild
            # ref: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html
            if os.environ.get(CODE_BUILD_BUILD_ID_KEY):
                v = os.environ.get(CODE_BUILD_WEBHOOK_HEAD_REF_KEY)
                if v:
                    # refs/head/<branch name>
                    self.branch = v.split("/")[-1]

            if self.branch:
                return      # if we've figured this out, great

            try:
                show_ref = subprocess.check_output(["git", "show-ref"], cwd=self.dir).decode()
                refs = [ref for ref in show_ref.split("\n") if self.commit_hash in ref]

                if len(refs) > 0:
                    # We assume the following values:
                    # * ed6de84bde58d51deebe90e01ddfa5fa78899b1c refs/heads/branch/branch-name
                    # * ed6de84bde58d51deebe90e01ddfa5fa78899b1c refs/remotes/origin/branch-name
                    match = re.search('[a-f0-9]{40} refs/(heads|remotes/origin)/(.*)', refs[0])
                    if match:
                        self.branch = match.group(2)
                    else:
                        self.branch = refs[0].split("/")[-1]
            except Exception:
                # cannot get branch name by git command
                pass

    # The first order of business is to ascertain what Git repositories we have in the workspace
    def list_sources() -> List[Workspace]:
        # This command accepts REPO_NAME=REPO_DIR as well as just REPO_DIR
        pattern = re.compile(r'[^=]+=[^=]+')
        ws: List[Workspace] = []
        for s in source:
            if pattern.match(s):
                kv = s.split('=')
                ws.append(Workspace(name=kv[0], dir=kv[1]))
            else:
                ws.append(Workspace(name=s, dir=s))
            # TODO: if repo_dir is absolute path, warn the user that that's probably
            # not what they want to do
        return ws

    # `record commit` on each top-level (= non submodule) Git repository
    # `record commit` command processes Git submodule on its own,
    # so we need to do this between list_sources and list_submodules
    def collect_commits():
        if not no_commit_collection:
            for w in ws:
                commit(ctx, source=w.dir, max_days=max_days)
        else:
            typer.secho(
                "Warning: Commit collection is turned off. The commit data must be collected separately.",
                fg=typer.colors.YELLOW, err=True)

    # tally up all the submodules, unless we are told not to
    def list_submodules(workspaces: List[Workspace]) -> List[Workspace]:
        if no_submodules:
            return workspaces

        r = workspaces.copy()
        for w in workspaces:
            submodule_pattern = re.compile(r"^[\+\-U ](?P<hash>[a-f0-9]{40}) (?P<name>\S+)")

            # invoke git directly because dulwich's submodule feature was broken
            submodule_stdouts = subprocess.check_output("git submodule status --recursive".split(),
                                                        cwd=w.dir).decode().splitlines()
            for submodule_stdout in submodule_stdouts:
                # the output is e.g.
                # "+bbf213437a65e82dd6dda4391ecc5d598200a6ce sub1 (heads/master)"
                matched = submodule_pattern.search(submodule_stdout)
                if matched:
                    commit_hash = matched.group('hash')
                    name = matched.group('name')
                    if commit_hash and name:
                        r.append(Workspace(
                            name=w.name + "/" + name,
                            dir=w.dir + "/" + name,
                            commit_hash=commit_hash))
        return r

    # figure out the commit hash and branch of those workspaces
    def compute_hash_and_branch(ws: List[Workspace]):
        ws_by_name = {w.name: w for w in ws}

        # Process repository options to create branch name mappings
        branch_name_map = dict()
        if len(repositories) == 1 and len(ws) == 1 and not ('=' in repositories[0]):
            # if there's only one repo and the short form "--repository NAME" is used, then we assign that to the first repo
            branch_name_map[ws[0].name] = repositories[0]
        else:
            for r in repositories:
                kv = r.split('=')
                if len(kv) != 2:
                    typer.secho(
                        f"Expected --repo-branch-map REPO=BRANCHNAME but got {kv}",
                        fg=typer.colors.YELLOW, err=True)
                    raise typer.Exit(1)

                if not ws_by_name.get(kv[0]):
                    typer.secho(
                        f"Invalid repository name {kv[0]} in a --repo-branch-map option. ",
                        fg=typer.colors.YELLOW, err=True)
                    # TODO: is there any reason this is not an error? for now erring on caution
                    # sys.exit(1)

                branch_name_map[kv[0]] = kv[1]

        for w in ws:
            try:
                if not w.commit_hash:
                    w.commit_hash = subprocess.check_output("git rev-parse HEAD".split(), cwd=w.dir).decode().replace("\n", "")
            except Exception as e:
                typer.secho(
                    "Can't get commit hash for {}. Do you run command under git-controlled directory? "
                    "If not, please set a directory use by --source option.",
                    fg=typer.colors.YELLOW, err=True)
                print(e, file=sys.stderr)
                raise typer.Exit(1)
            if w.name in branch_name_map:
                w.branch = branch_name_map[w.name]
            else:
                w.calc_branch_name()

    # Rely on --commit to create a list of workspaces, even when there's no local Git workspaces
    def synthesize_workspaces() -> List[Workspace]:
        ws = []

        commit_pattern = re.compile("[0-9A-Fa-f]{5,40}$")

        for name, hash in parsed_commits:
            if not commit_pattern.match(hash):
                typer.secho(
                    f"{name}'s commit hash `{hash}` is invalid.",
                    fg=typer.colors.YELLOW, err=True)
                raise typer.Exit(1)

            ws.append(Workspace(name=name, commit_hash=hash))

        return ws

    # send all the data to server and obtain build_id, or none if the service is down, to recover
    def send(ws: List[Workspace]) -> str | None:
        # figure out all the CI links to capture
        def compute_links():
            _links = capture_link(os.environ)
            return _links

        tracking_client = TrackingClient(Tracking.Command.RECORD_BUILD, app=app)
        client = LaunchableClient(app=app, tracking_client=tracking_client)
        try:
            lineage = branch or ws[0].branch
            if lineage is None:
                typer.echo("Unable to determine branch name. Please specify --branch option.", err=True)
                raise typer.Exit(1)

            payload = {
                "buildNumber": build_name,
                "lineage": lineage,
                "commitHashes": [{
                    'repositoryName': w.name,
                    'commitHash': w.commit_hash,
                    'branchName': w.branch or ""
                } for w in ws],
                "links": compute_links(),
                "timestamp": parsed_timestamp.isoformat() if parsed_timestamp else None,
            }

            res = client.request("post", "builds", payload=payload)
            res.raise_for_status()

            return res.json().get("id", None)
        except Exception as e:
            tracking_client.send_error_event(
                event_name=Tracking.ErrorEvent.INTERNAL_CLI_ERROR,
                stack_trace=str(e),
            )
            client.print_exception_and_recover(e)
            return None

    # report what we did to the user to assist diagnostics
    def report(ws: List[Workspace], build_id: str):
        org, workspace = get_org_workspace()
        typer.echo(
            f"Launchable recorded build {build_name} to workspace {org}/{workspace} with commits from {
                len(ws)} {
                'repositories' if len(ws) > 1 else 'repository'}:\n")

        header = ["Name", "Path", "HEAD Commit"]
        rows = [[w.name, w.dir, w.commit_hash] for w in ws]
        typer.echo(tabulate(rows, header, tablefmt="github"))
        typer.echo(
            f"\nVisit https://app.launchableinc.com/organizations/{org}/workspaces/"
            f"{workspace}/data/builds/{build_id} to view this build and its test sessions")

    # all the logics at the high level
    if len(commits) == 0:
        ws = list_sources()
        collect_commits()
        ws = list_submodules(ws)
    else:
        ws = synthesize_workspaces()
    compute_hash_and_branch(ws)
    build_id = send(ws)
    if not build_id:
        return  # recover from service outage gracefully
    report(ws, build_id)
