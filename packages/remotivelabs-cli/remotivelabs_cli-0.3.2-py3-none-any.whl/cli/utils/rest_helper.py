from __future__ import annotations

import base64
import json
import logging
import os
import shutil
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union, cast

import requests
from requests.exceptions import JSONDecodeError
from rich.progress import Progress, SpinnerColumn, TextColumn, wrap_file

from cli.settings import settings
from cli.utils import versions
from cli.utils.console import print_generic_error, print_generic_message, print_hint, print_unformatted, print_unformatted_to_stderr

if "REMOTIVE_CLOUD_HTTP_LOGGING" in os.environ:
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


class RestHelper:
    """Static Class with various helper functions for the rest API"""

    __base_url = "https://cloud.remotivelabs.com"
    __frontend_url = __base_url
    __license_server_base_url = "https://license.cloud.remotivelabs.com"

    if "REMOTIVE_CLOUD_BASE_URL" in os.environ:
        __base_url = os.environ["REMOTIVE_CLOUD_BASE_URL"]
        __frontend_url = os.environ["REMOTIVE_CLOUD_BASE_URL"]

    if "REMOTIVE_CLOUD_FRONTEND_BASE_URL" in os.environ:
        __frontend_url = os.environ["REMOTIVE_CLOUD_FRONTEND_BASE_URL"]

    if "cloud-dev" in __base_url:
        __license_server_base_url = "https://license.cloud-dev.remotivelabs.com"

    __headers: Dict[str, str] = {"User-Agent": f"remotivelabs-cli/{versions.cli_version()} ({versions.platform_info()})"}
    __org: str = ""

    __token: str = ""

    def _cli_version(self) -> str:
        return ""

    @staticmethod
    def get_cli_version() -> str:
        return version("remotivelabs-cli")

    @staticmethod
    def get_base_url() -> str:
        return RestHelper.__base_url

    @staticmethod
    def get_base_frontend_url() -> str:
        return RestHelper.__frontend_url

    @staticmethod
    def get_license_server_base_url() -> str:
        return RestHelper.__license_server_base_url

    @staticmethod
    def get_headers() -> Dict[str, str]:
        return RestHelper.__headers

    @staticmethod
    def get_org() -> str:
        return RestHelper.__org

    @staticmethod
    def get_token() -> str:
        return RestHelper.__token

    @staticmethod
    def ensure_auth_token(quiet: bool = False, access_token: Optional[str] = None) -> None:
        """
        TODO: remove setting org, as we already set the default organization as env in remotive.py?
        TODO: don't sys.exit, raise error instead
        """
        if "REMOTIVE_CLOUD_ORGANIZATION" not in os.environ:
            active_account = settings.get_active_account()
            if active_account:
                org = active_account.default_organization
                if org:
                    os.environ["REMOTIVE_CLOUD_ORGANIZATION"] = org

        token = access_token
        if not token:
            token = os.environ.get("REMOTIVE_CLOUD_ACCESS_TOKEN", settings.get_active_token())
            if not token:
                if quiet:
                    return
                print_hint("you are not logged in, please login using [green]remotive cloud auth login[/green]")
                sys.exit(1)

        RestHelper.__headers["Authorization"] = f"Bearer {token.strip()}"

    @staticmethod
    def handle_get(  # noqa: PLR0913
        url: str,
        params: Any = None,
        return_response: bool = False,
        allow_status_codes: List[int] | None = None,
        progress_label: str = "Fetching...",
        use_progress_indicator: bool = True,
        allow_redirects: bool = False,
        timeout: int = 60,
        access_token: Optional[str] = None,
        skip_access_token: bool = False,
    ) -> requests.Response:
        # Returns a Response object if succesfull otherwise None
        if params is None:
            params = {}
        if not skip_access_token:
            RestHelper.ensure_auth_token(access_token=access_token)
        if use_progress_indicator:
            with RestHelper.use_progress(progress_label):
                r = requests.get(
                    f"{RestHelper.__base_url}{url}",
                    headers=RestHelper.__headers,
                    params=params,
                    timeout=timeout,
                    allow_redirects=allow_redirects,
                )
        else:
            r = requests.get(
                f"{RestHelper.__base_url}{url}",
                headers=RestHelper.__headers,
                params=params,
                timeout=timeout,
                allow_redirects=allow_redirects,
            )

        if return_response:
            RestHelper.check_api_result(r, allow_status_codes)
            return r
        RestHelper.print_api_result(r)
        sys.exit(0)

    @staticmethod
    def has_access(url: str, params: Any = {}, access_token: Optional[str] = None) -> bool:
        RestHelper.ensure_auth_token(quiet=True, access_token=access_token)
        r = requests.get(f"{RestHelper.__base_url}{url}", headers=RestHelper.__headers, params=params, timeout=60)
        if 200 <= r.status_code <= 299:
            return True
        return False

    @staticmethod
    def check_api_result(response: requests.Response, allow_status_codes: List[int] | None = None) -> None:
        """
        TODO: don't sys.exit, raise error instead
        """
        if response.status_code == 426:  # CLI upgrade
            print_hint(response.text)
            sys.exit(1)
        if response.status_code > 299:
            if allow_status_codes is not None and response.status_code in allow_status_codes:
                return
            print_generic_error(f"Got status code: {response.status_code}")
            if response.status_code == 401:
                print_generic_message("Your token is not valid or has expired, please login again or activate another account")
            else:
                print_unformatted_to_stderr(response.text)
            sys.exit(1)

    @staticmethod
    def print_api_result(response: requests.Response) -> None:
        """
        TODO: don't sys.exit, raise error instead
        TODO: dont print from here, return and let caller print instead
        """
        if response.status_code == 426:  # CLI upgrade
            print_hint(response.text)
            sys.exit(1)

        if response.status_code >= 200 and response.status_code < 300:
            if len(response.content) >= 2:
                try:
                    print_unformatted(json.dumps(response.json()))
                except JSONDecodeError:
                    print_generic_error("Json parse error: Please try again and report if the error persists")
            sys.exit(0)
        else:
            print_generic_error(f"Got status code: {response.status_code}")
            if response.status_code == 401:
                print_generic_message("Your token is not valid or has expired, please login again or activate another account")
            else:
                print_unformatted_to_stderr(response.text)
            sys.exit(1)

    @staticmethod
    def handle_patch(  # noqa: PLR0913
        url: str,
        params: Any = {},
        quiet: bool = False,
        progress_label: str = "Deleting...",
        access_token: Optional[str] = None,
        allow_status_codes: Optional[List[int]] = None,
    ) -> requests.Response:
        if allow_status_codes is None:
            allow_status_codes = []
        RestHelper.ensure_auth_token(access_token=access_token)
        with RestHelper.use_progress(progress_label):
            r = requests.patch(f"{RestHelper.__base_url}{url}", headers=RestHelper.__headers, params=params, timeout=60)
        if r.status_code in (200, 204):
            if not quiet:
                RestHelper.print_api_result(r)
        elif r.status_code not in allow_status_codes:
            RestHelper.print_api_result(r)
        return r

    @staticmethod
    def handle_delete(  # noqa: PLR0913
        url: str,
        params: Any = {},
        quiet: bool = False,
        progress_label: str = "Deleting...",
        access_token: Optional[str] = None,
        allow_status_codes: Optional[List[int]] = None,
    ) -> requests.Response:
        if allow_status_codes is None:
            allow_status_codes = []
        RestHelper.ensure_auth_token(access_token=access_token)
        with RestHelper.use_progress(progress_label):
            r = requests.delete(f"{RestHelper.__base_url}{url}", headers=RestHelper.__headers, params=params, timeout=60)
        if r.status_code in (200, 204):
            if not quiet:
                RestHelper.print_api_result(r)
        elif r.status_code not in allow_status_codes:
            RestHelper.print_api_result(r)
        return r

    @staticmethod
    def handle_post(  # noqa: PLR0913
        url: str,
        body: Any = None,
        params: Any = {},
        progress_label: str = "Processing...",
        return_response: bool = False,
        access_token: Optional[str] = None,
    ) -> requests.Response:
        # Returns a Response object if succesfull otherwise, None

        RestHelper.ensure_auth_token(access_token=access_token)
        RestHelper.__headers["content-type"] = "application/json"

        with RestHelper.use_progress(progress_label):
            r = requests.post(f"{RestHelper.__base_url}{url}", headers=RestHelper.__headers, params=params, data=body, timeout=60)

        if return_response:
            RestHelper.check_api_result(r)
            return r

        RestHelper.print_api_result(r)
        sys.exit(0)

    @staticmethod
    def handle_put(url: str, body: Any = None, params: Any = {}, return_response: bool = False) -> requests.Response | None:
        # Returns a Response object if succesfull otherwise, None
        RestHelper.ensure_auth_token()
        RestHelper.__headers["content-type"] = "application/json"
        r = requests.put(f"{RestHelper.__base_url}{url}", headers=RestHelper.__headers, params=params, data=body, timeout=60)

        if return_response:
            RestHelper.check_api_result(r)
            return r
        RestHelper.print_api_result(r)
        return None

    @staticmethod
    def upload_file(
        path: Union[str, Path],
        url: str,
        upload_headers: Dict[str, str] | None = None,
        return_response: bool = False,
        progress_label: str = "Uploading...",
    ) -> requests.Response | None:
        # Returns a Response object if succesfull otherwise, None
        RestHelper.ensure_auth_token()
        if upload_headers is not None:
            RestHelper.__headers.update(upload_headers)
        with open(path, "rb") as file:
            with wrap_file(file, os.stat(path).st_size, description=progress_label) as f:
                r = requests.post(
                    f"{RestHelper.__base_url}{url}", files={os.path.basename(path): f}, headers=RestHelper.__headers, timeout=60
                )
            if return_response:
                RestHelper.check_api_result(r)
                return r
            RestHelper.print_api_result(r)
        return None

    @staticmethod
    def upload_file_with_signed_url(
        path: Union[str, Path],
        url: str,
        upload_headers: Dict[str, str],
        return_response: bool = False,
        progress_label: str = "Uploading...",
    ) -> requests.Response | None:
        # Returns a Response object if succesfull otherwise, None
        with open(path, "rb") as file:
            with wrap_file(file, os.stat(path).st_size, description=progress_label, transient=False) as f:
                r = requests.put(url, data=f, headers=upload_headers, timeout=60)
            if return_response:
                RestHelper.check_api_result(r)
                return r
            RestHelper.print_api_result(r)
        return None

    @staticmethod
    def use_progress(label: str, transient: bool = True) -> Progress:
        p = Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=transient)
        p.add_task(label, total=1)
        return p

    @staticmethod
    def download_file(save_file_name: Path, url: str) -> None:
        # Next download the actual file
        download_resp = requests.get(url=url, stream=True, timeout=60)
        if download_resp.status_code == 200:
            content_length = int(download_resp.headers["Content-Length"])
            with open(save_file_name, "wb") as out_file:
                stream = cast(BinaryIO, download_resp.raw)  # we know this is a binary stream, as stream=True is set in the request
                with wrap_file(
                    stream,
                    content_length,
                    refresh_per_second=100,
                    description=f"Downloading to {save_file_name}",
                ) as stream_with_progress:
                    shutil.copyfileobj(stream_with_progress, out_file)
        else:
            RestHelper.check_api_result(download_resp)

    @staticmethod
    def request_license(email: str, machine_id: Dict[str, Any]) -> str:
        # Lets keep the email here so we have the same interface for both authenticated
        # and not authenticated license requests.
        # email will be validated in the license server to make sure it matches with the user of the
        # access token so not any email is sent here
        RestHelper.ensure_auth_token()
        payload = {"id": email, "machine_id": machine_id}
        b64_encoded_bytes = base64.encodebytes(json.dumps(payload).encode())
        license_jsonb64 = {"licensejsonb64": b64_encoded_bytes.decode("utf-8")}
        RestHelper.__headers["content-type"] = "application/json"
        r = requests.post(
            url=f"{RestHelper.__license_server_base_url}/api/license/request",
            headers=RestHelper.__headers,
            data=json.dumps(license_jsonb64),
            timeout=60,
        )
        RestHelper.check_api_result(r)
        return str(r.json()["license_data"])
