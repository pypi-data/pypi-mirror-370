import os
from typing import BinaryIO

import requests
import typer
from requests import HTTPError, Session, Timeout

from smart_tests.utils.http_client import _HttpClient, _join_paths
from smart_tests.utils.tracking import Tracking, TrackingClient  # type: ignore

from ..app import Application
from .authentication import get_org_workspace
from .env_keys import REPORT_ERROR_KEY


class LaunchableClient:
    def __init__(self, tracking_client: TrackingClient | None = None, base_url: str = "", session: Session | None = None,
                 test_runner: str | None = "", app: Application | None = None):
        self.http_client = _HttpClient(
            base_url=base_url,
            session=session,
            test_runner=test_runner,
            app=app
        )
        self.tracking_client = tracking_client
        self.organization, self.workspace = get_org_workspace()
        if self.organization is None or self.workspace is None:
            raise ValueError(
                "Could not identify a Smart Tests organization/workspace. "
                "Confirm that you set SMART_TESTS_TOKEN "
                "(or SMART_TESTS_ORGANIZATION and SMART_TESTS_WORKSPACE) environment variable(s)\n"
                "See https://docs.launchableinc.com/getting-started#setting-your-api-key")

    def request(
        self,
        method: str,
        sub_path: str,
        payload: dict | BinaryIO | None = None,
        params: dict | None = None,
        timeout: tuple[int, int] = (5, 60),
        compress: bool = False,
        additional_headers: dict | None = None,
    ) -> requests.Response:
        path = _join_paths(
            f"/intake/organizations/{self.organization}/workspaces/{self.workspace}",
            sub_path
        )

        # report an error and bail out
        def track(event_name: Tracking.ErrorEvent, e: Exception):
            if self.tracking_client:
                self.tracking_client.send_error_event(
                    event_name=event_name,
                    stack_trace=str(e),
                    api=sub_path,
                )
            raise e

        try:
            response = self.http_client.request(
                method=method,
                path=path,
                payload=payload,
                params=params,
                timeout=timeout,
                compress=compress,
                additional_headers=additional_headers
            )
            return response
        except ConnectionError as e:
            track(Tracking.ErrorEvent.NETWORK_ERROR, e)
        except Timeout as e:
            track(Tracking.ErrorEvent.TIMEOUT_ERROR, e)
        except HTTPError as e:
            track(Tracking.ErrorEvent.UNEXPECTED_HTTP_STATUS_ERROR, e)
        except Exception as e:
            track(Tracking.ErrorEvent.INTERNAL_SERVER_ERROR, e)

        # should never come here, but needed to make type checker happy
        assert False

    def print_exception_and_recover(self, e: Exception, warning: str | None = None, warning_color='yellow'):
        """
        Print the exception raised from the request method, then recover from it

        :param warning: optional warning message to contextualize the HTTP error
        """

        # a diagnostics flag to abort and report the details
        if os.getenv(REPORT_ERROR_KEY):
            raise e

        typer.echo(e, err=True)
        if isinstance(e, HTTPError):
            # if the payload is present, report that as well to assist troubleshooting
            res = e.response
            if res and res.text:
                typer.echo(res.text, err=True)

        if warning:
            typer.secho(warning, fg=getattr(typer.colors, warning_color.upper(), typer.colors.YELLOW), err=True)

    def set_test_runner(self, test_runner: str):
        """Update the test runner name for this client."""
        self.http_client.test_runner = test_runner
