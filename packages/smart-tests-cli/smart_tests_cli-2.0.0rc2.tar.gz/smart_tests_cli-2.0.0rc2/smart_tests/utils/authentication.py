import os
from typing import Tuple

import requests
import typer

from .env_keys import ORGANIZATION_KEY, WORKSPACE_KEY, get_token


def get_org_workspace():
    token = get_token()
    if token:
        try:
            _, user, _ = token.split(":", 2)
            org, workspace = user.split("/", 1)
            return org, workspace
        except ValueError:
            return None, None

    return os.getenv(ORGANIZATION_KEY), os.getenv(WORKSPACE_KEY)


def ensure_org_workspace() -> Tuple[str, str]:
    org, workspace = get_org_workspace()
    if org is None or workspace is None:
        typer.secho(
            "Could not identify Smart Tests organization/workspace. "
            "Please confirm if you set SMART_TESTS_TOKEN "
            "(or LAUNCHABLE_TOKEN for backward compatibility) or SMART_TESTS_ORGANIZATION and "
            "SMART_TESTS_WORKSPACE environment variables", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    return org, workspace


def authentication_headers():
    token = get_token()
    if token:
        return {'Authorization': f'Bearer {token}'}

    if os.getenv('EXPERIMENTAL_GITHUB_OIDC_TOKEN_AUTH'):
        req_url = os.getenv('ACTIONS_ID_TOKEN_REQUEST_URL')
        rt_token = os.getenv('ACTIONS_ID_TOKEN_REQUEST_TOKEN')
        if not req_url or not rt_token:
            typer.secho(
                "GitHub Actions OIDC tokens cannot be retrieved."
                "Confirm that you have added necessary permissions following "
                "https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-cloud-providers#adding-permissions-settings",  # noqa: E501
                fg=typer.colors.RED, err=True)
            raise typer.Exit(1)
        r = requests.get(req_url,
                         headers={
                             'Authorization': f'Bearer {rt_token}',
                             'Accept': 'application/json; api-version=2.0',
                             'Content-Type': 'application/json',
                         })
        r.raise_for_status()
        return {"Authorization": f"Bearer {r.json()["value"]}"}

    if os.getenv('GITHUB_ACTIONS'):
        headers = {
            'GitHub-Actions': os.environ['GITHUB_ACTIONS'],
            'GitHub-Run-Id': os.environ['GITHUB_RUN_ID'],
            'GitHub-Repository': os.environ['GITHUB_REPOSITORY'],
            'GitHub-Workflow': os.environ['GITHUB_WORKFLOW'],
            'GitHub-Run-Number': os.environ['GITHUB_RUN_NUMBER'],
            'GitHub-Event-Name': os.environ['GITHUB_EVENT_NAME'],
            'GitHub-Sha': os.environ['GITHUB_SHA'],
        }

        # GITHUB_PR_HEAD_SHA might not exist
        pr_head_sha = os.getenv('GITHUB_PR_HEAD_SHA')
        if pr_head_sha:
            headers['GitHub-Pr-Head-Sha'] = pr_head_sha

        return headers
    return {}
