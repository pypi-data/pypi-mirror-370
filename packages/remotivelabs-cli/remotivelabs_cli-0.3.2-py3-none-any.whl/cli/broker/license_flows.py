from __future__ import annotations

import json
import time
from typing import Union

import grpc
import requests
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from cli.broker.lib.broker import Broker, LicenseInfo
from cli.utils.console import print_unformatted_to_stderr
from cli.utils.rest_helper import RestHelper as Rest


class LicenseFlow:
    def describe_with_url(self, url: str) -> LicenseInfo:
        b = LicenseFlow.__try_connect_to_broker(
            url=url,
            progress_label=f"Fetching license from broker ({url})...",
            on_error_progress_label=f"Fetching license from broker ({url})... make sure broker is running.",
        )
        return b.get_license()

    def describe_with_hotspot(self, url: Union[str, None] = "http://192.168.4.1:50051") -> LicenseInfo:
        if url is None:
            url = "http://192.168.4.1:50051"

        b = LicenseFlow.__try_connect_to_broker(
            url=url, progress_label=f"Fetching license from broker using hotspot ({url})... Make sure to switch to remotivelabs-xxx Wi-Fi"
        )
        return b.get_license()

    def request_with_url_with_internet(self, url: str) -> None:
        print_unformatted_to_stderr("This requires internet connection from your computer during the entire licensing process")

        email = LicenseFlow.__try_authenticate_and_get_email_from_cloud()

        broker_to_license = LicenseFlow.__try_connect_to_broker(
            url=url,
            progress_label=f"Fetching existing broker license...({url})...",
        )

        existing_license = broker_to_license.get_license()
        if existing_license.valid:
            apply = typer.confirm(
                f"This broker already has a valid license, and is licensed to {existing_license.email}. Do you still wish to proceed?"
            )
            if not apply:
                return

        print_unformatted_to_stderr(
            ":point_right: [bold yellow]This will request a new license or use an existing license if "
            "this hardware has already been licensed[/bold yellow]"
        )
        apply_license = typer.confirm("Do you want to continue and agree to terms and conditions at https://remotivelabs.com/license?")
        if not apply_license:
            return

        existing_license = broker_to_license.get_license()
        license_data_b64 = LicenseFlow.__try_request_license(email, existing_license, "Requesting license...")

        with use_progress("Applying license to broker..."):
            new_license = broker_to_license.apply_license(license_data_b64)
        if new_license.valid:
            print_unformatted_to_stderr(f":thumbsup: Successfully applied license, it remains valid until {new_license.expires}")

    def request_with_hotspot(self, url: Union[str, None] = "http://192.168.4.1:50051") -> None:
        """
        This flow expects changes between networks and tries to guide the user accordingly
        :param url: If None it will use the default hotspot IP
        """
        if url is None:
            url = "http://192.168.4.1:50051"

        print_unformatted_to_stderr(
            "Licensing a broker over its wifi hotspot will require you to switch between internet connectivity "
            "and remotivelabs-xxx wifi hotspot"
        )

        email = LicenseFlow.__try_authenticate_and_get_email_from_cloud()

        broker_to_license = LicenseFlow.__try_connect_to_broker(
            url=url,
            progress_label=f"Fetching license from broker using hotspot ({url})... Make sure to switch to remotivelabs-xxx wifi",
        )
        existing_license = broker_to_license.get_license()
        if existing_license.valid:
            apply = typer.confirm(
                f"This broker already has a valid license and is licensed to {existing_license.email}. Do you still wish to proceed?"
            )
            if not apply:
                return

        print_unformatted_to_stderr(
            ":point_right: [bold yellow]This will request a new license or use an existing license if "
            "this hardware has already been licensed[/bold yellow]"
        )
        apply_license = typer.confirm("Do you want to continue and agree to terms and conditions at https://remotivelabs.com/license?")
        if not apply_license:
            return

        license_data_b64 = LicenseFlow.__try_request_license(email, existing_license)

        broker_to_license = LicenseFlow.__try_connect_to_broker(
            url=url,
            progress_label="Applying license to broker...  Make sure to switch back to remotivelabs-xxx wifi hotspot",
        )
        new_license = broker_to_license.apply_license(license_data_b64)
        print_unformatted_to_stderr(f":thumbsup: Successfully applied license, expires {new_license.expires}")

    @staticmethod
    def __try_connect_to_broker(url: str, progress_label: str, on_error_progress_label: Union[str, None] = None) -> Broker:
        with use_progress(progress_label) as p:
            while True:
                try:
                    broker_to_license = Broker(url=url)
                    break
                except grpc.RpcError:
                    if on_error_progress_label is not None:
                        p.update(
                            p.task_ids[0],
                            description=on_error_progress_label,
                        )
                    time.sleep(1)
        if on_error_progress_label is None:
            print_unformatted_to_stderr(f":white_check_mark: {progress_label}")
        else:
            print_unformatted_to_stderr(f":white_check_mark: {on_error_progress_label}")
        return broker_to_license

    @staticmethod
    def __try_authenticate_and_get_email_from_cloud() -> str:
        with use_progress("Fetching user info from cloud... Make sure you are connected to internet"):
            while True:
                try:
                    r = Rest.handle_get("/api/whoami", return_response=True, use_progress_indicator=False, timeout=5)
                    break
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    time.sleep(1)
        print_unformatted_to_stderr(":white_check_mark: Fetching user info from cloud... Make sure you are connected to internet")
        if r is None:
            return ""
        return str(r.json()["email"])

    @staticmethod
    def __try_request_license(
        email: str,
        existing_license: LicenseInfo,
        progress_label: str = "Requesting license... make sure to switch back to network with internet access",
    ) -> bytes:
        with use_progress(progress_label):
            while True:
                try:
                    license_data_b64 = Rest.request_license(email, json.loads(existing_license.machine_id)).encode()
                    break
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                    time.sleep(1)
        print_unformatted_to_stderr(f":white_check_mark: {progress_label}")
        return bytes(license_data_b64)


def use_progress(label: str) -> Progress:
    p = Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True, expand=False)
    p.add_task(label, total=1)
    return p
