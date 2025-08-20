from __future__ import annotations

import base64
import hashlib
import os
import secrets
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import typer
from typing_extensions import override

from cli.cloud.auth_tokens import do_activate, prompt_to_set_org
from cli.settings import settings
from cli.settings.token_file import TokenFile
from cli.utils.console import print_generic_error, print_newline, print_success, print_unformatted, print_url
from cli.utils.rest_helper import RestHelper as Rest

httpd: HTTPServer


def generate_pkce_pair() -> Tuple[str, str]:
    """
    PKCE is used for all cli login flows, both headless and browser.
    """
    code_verifier_ = secrets.token_urlsafe(64)  # High-entropy string
    code_challenge_ = base64.urlsafe_b64encode(hashlib.sha256(code_verifier_.encode("ascii")).digest()).rstrip(b"=").decode("ascii")
    return code_verifier_, code_challenge_


code_verifier, code_challenge = generate_pkce_pair()
state = secrets.token_urlsafe(16)

short_lived_token = None


class S(BaseHTTPRequestHandler):
    def _set_response(self) -> None:
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    @override
    def log_message(self, format: Any, *args: Any) -> None:
        return

    # Please do not change this into lowercase!
    @override
    def do_GET(self) -> None:  # type: ignore # noqa: PLR0912
        self._set_response()

        parsed_url = urlparse(self.path)

        # Get query parameters as a dict
        query_params = parse_qs(parsed_url.query)

        # Example: Get the value of the "error" parameter if it exists
        error_value = query_params.get("error", [None])[0]
        path = self.path
        auth_code = path[1:]  # Remotive /
        time.sleep(1)
        httpd.server_close()

        killerthread = Thread(target=httpd.shutdown)
        killerthread.start()
        if error_value is None:
            res = Rest.handle_get(
                f"/api/open/token?code={auth_code}&code_verifier={code_verifier}",
                return_response=True,
                skip_access_token=True,
                allow_status_codes=[401, 400],
            )
            if res.status_code != 200:
                print_generic_error(
                    "Failed to fetch token. Please try again, if the problem persists please reach out to support@remotivelabs.com"
                )
                self.wfile.write(
                    "Failed to fetch token. Please try again, if the problem persists please reach out to support@remotivelabs.com".encode(
                        "utf-8"
                    )
                )
                sys.exit(1)

            # TODO - This is written before we are done...
            self.wfile.write(
                """Successfully setup CLI, you may close this window now. Return to your terminal to continue""".encode("utf-8")
            )
            access_token = res.json()["access_token"]
            global short_lived_token  # noqa: PLW0603
            short_lived_token = access_token

        else:
            if error_value == "no_consent":
                self.wfile.write(
                    """
                Authorization was cancelled.<br/>
                To use RemotiveCLI, you need to grant access to your RemotiveCloud account.
                <br/><br/>
                Run `remotive cloud auth login` to try again.
                """.encode("utf-8")
                )
                print_generic_error("You did not grant access to RemotiveCloud, login aborted")
            elif error_value == "user_not_exists":
                self.wfile.write(
                    """
                It seems like you do not have an account at RemotiveCloud with that user<br/>
                To use RemotiveCLI you must first sign up at <a href="https://cloud.remotivelabs.com">cloud.remotivelabs.com</a>
                and approve our agreements.<br/>
                <br/><br/>
                Once you are signed up, Run `remotive cloud auth login` again.
                """.encode("utf-8")
                )
                print_generic_error(
                    "To use RemotiveCLI you must first sign up at https://cloud.remotivelabs.com and approve our agreements"
                )
            else:
                self.wfile.write(f"Unknown error {error_value}, please contact support@remotivelabs.com".encode("utf-8"))
                print_generic_error(f"Unexpected error {error_value}, please contact support@remotivelabs.com")
            sys.exit(1)


def prepare_local_webserver(server_class: type = HTTPServer, handler_class: type = S, port: Optional[int] = None) -> None:
    if port is None:
        env_val = os.getenv("REMOTIVE_LOGIN_CALLBACK_PORT" or "")
        port = int(env_val) if env_val and env_val.isdigit() else 0

    server_address = ("", port)
    global httpd  # noqa: PLW0603
    httpd = server_class(server_address, handler_class)


def create_personal_token() -> None:
    response = Rest.handle_post(
        url="/api/me/keys",
        return_response=True,
        access_token=short_lived_token,
        # TODO - add body with alias
    )
    token = response.json()
    email = token["account"]["email"]
    existing_file = settings.get_token_file_by_email(email=email)
    if existing_file is not None:
        res = Rest.handle_patch(
            f"/api/me/keys/{existing_file.name}/revoke",
            quiet=True,
            access_token=short_lived_token,
            allow_status_codes=[400, 404],
        )
        if res is not None and res.status_code == 204:
            Rest.handle_delete(
                f"/api/me/keys/{existing_file.name}",
                quiet=True,
                access_token=short_lived_token,
            )
        settings.remove_token_file(existing_file.name)

    settings.add_personal_token(response.text, activate=True)

    print_success("Logged in")


def _do_prompt_to_use_existing_credentials() -> Optional[TokenFile]:
    token_files = settings.list_personal_token_files()
    if len(token_files) > 0:
        should_select_token = typer.confirm(
            "You have credentials available already, would you like to choose one of these instead?", default=True
        )
        if should_select_token:
            token = do_activate(token_name=None)
            if token is not None:
                return token
            # TODO - fix so this is not needed
            sys.exit(0)
    return None


def login(headless: bool = False) -> bool:  # noqa: C901, PLR0915
    """
    Initiate login
    """

    #
    # Check login.md flowchart for better understanding
    #

    active_token_file = settings.get_active_token_file()
    if active_token_file:
        # check if the active token is valid, if not, prompt user to select a new token
        if not Rest.has_access("/api/whoami") or active_token_file.is_expired():
            settings.clear_active_account()
            newly_activated_token_file = _do_prompt_to_use_existing_credentials()
            if newly_activated_token_file:
                return True

            # intentional fall through to login since we have no token

    else:
        # no active token, prompt user to select a new token
        newly_activated_token_file = _do_prompt_to_use_existing_credentials()
        if newly_activated_token_file:
            return True

        # intentional fall through to login since we have no token

    #
    # 2. Login in if no valid token found...
    #

    prepare_local_webserver()

    def force_use_webserver_callback() -> bool:
        env_val = os.getenv("REMOTIVE_LOGIN_FORCE_CALLBACK" or "no")
        if env_val and env_val == "yes":
            return True
        return False

    def login_with_callback_but_copy_url() -> None:
        """
        This will print a url the will trigger a callback later so the webserver must be up and running.
        """
        print_unformatted("Copy the following link in a browser to login to cloud, and complete the sign-in prompts:")
        print_newline()

        url = (
            f"{Rest.get_base_frontend_url()}/login"
            f"?state={state}"
            f"&cli_version={Rest.get_cli_version()}"
            f"&response_type=code"
            f"&code_challenge={code_challenge}"
            f"&redirect_uri=http://localhost:{httpd.server_address[1]}"
        )
        print_url(url)
        httpd.serve_forever()

    def login_headless() -> None:
        """
        Full headless, opens a browser and expects a auth code to be entered and exchanged for the token
        """
        print_unformatted("Copy the following link in a browser to login to cloud, and complete the sign-in prompts:")
        print_newline()

        url = (
            f"{Rest.get_base_frontend_url()}/login"
            f"?state={state}"
            f"&cli_version={Rest.get_cli_version()}"
            f"&response_type=code"
            f"&code_challenge={code_challenge}"
        )
        print_url(url)

        code = typer.prompt(
            "Once finished, enter the verification code provided in your browser",
            hide_input=False,
        )
        res = Rest.handle_get(
            f"/api/open/token?code={code}&code_verifier={code_verifier}",
            return_response=True,
            skip_access_token=True,
            allow_status_codes=[401],
        )
        if res.status_code == 401:
            print_generic_error(
                "Failed to fetch token. Please try again, if the problem persists please reach out to support@remotivelabs.com"
            )
            sys.exit(1)
        access_token = res.json()["access_token"]
        global short_lived_token  # noqa: PLW0603
        short_lived_token = access_token
        create_personal_token()
        prompt_to_set_org()

    if headless and not force_use_webserver_callback():
        login_headless()
    elif headless and force_use_webserver_callback():
        login_with_callback_but_copy_url()
    else:
        could_open = webbrowser.open_new_tab(
            f"{Rest.get_base_frontend_url()}/login"
            f"?state={state}"
            f"&cli_version={Rest.get_cli_version()}"
            f"&response_type=code"
            f"&code_challenge={code_challenge}"
            f"&redirect_uri=http://localhost:{httpd.server_address[1]}"
        )

        if not could_open:
            print_generic_error(
                "Could not open a browser on this machine, this is likely because you are in an environment where no browser is available"
            )
            print_newline()
            if force_use_webserver_callback():
                login_with_callback_but_copy_url()
                create_personal_token()
            else:
                login_headless()
        else:
            httpd.serve_forever()
            create_personal_token()
            prompt_to_set_org()

    return True
