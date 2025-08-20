import dataclasses
import json
from enum import Enum

import typer
from rich import print_json

from cli.typer import typer_utils

from .license_flows import LicenseFlow

app = typer_utils.create_typer()

help_text = """
    More info on our docs page
    https://docs.remotivelabs.com/docs/remotive-broker/getting-started

    --connect describes how the connection is made to the broker and helps us properly connect to broker

      url      = Connects to the broker with the specified url, this is
      hotspot  = If you are using RemotiveBox (our reference hardware) you can connect to the
                 broker over its wifi hotspot. Getting the license from a RemotiveBox over its wifi hotspot
                 requires you switch wi-fi network to the RemotiveBox hotspot called 'remotivelabs-xxx' where
                 'xxx' is a random generated id.

    --url is the broker url, this is mandatory when connect type is "url"
    """


class Connection(str, Enum):
    hotspot = "hotspot"
    url = "url"
    # TODO - Support discover using mdns


@app.command()
def describe(
    connect: Connection = typer.Option("url", case_sensitive=False, help="How to connect to broker"),
    url: str = typer.Option("http://localhost:50051", is_eager=False, help="Broker URL", envvar="REMOTIVE_BROKER_URL"),
) -> None:
    """
    Show licence information

    More info on our docs page
    https://docs.remotivelabs.com/docs/remotive-broker/getting-started

    --connect describes how the connection is made to the broker and helps us properly connect to broker

    url      = Connects to the broker with the specified url, this is
    hotspot  = If you are using RemotiveBox (our reference hardware) you can connect to the
               broker over its wifi hotspot. Getting the license from a RemotiveBox over its wifi hotspot
               requires you switch wi-fi network to the RemotiveBox hotspot called 'remotivelabs-xxx' where
               'xxx' is a random generated id.

    --url is the broker url, this is mandatory when connect type is "url"
    """
    license_flow = LicenseFlow()
    if connect == Connection.url:
        existing_license = license_flow.describe_with_url(url)
        print_json(json.dumps(dataclasses.asdict(existing_license)))
    if connect == Connection.hotspot:
        existing_license = license_flow.describe_with_hotspot(url if url != "http://localhost:50051" else None)
        print_json(json.dumps(dataclasses.asdict(existing_license)))


@app.command()
def request(
    connect: Connection = typer.Option("url", case_sensitive=False, help="How to connect to broker"),
    url: str = typer.Option(
        "http://localhost:50051",
        is_eager=False,
        help="Broker url, this is mandatory when connect type is 'url'",
        envvar="REMOTIVE_BROKER_URL",
    ),
) -> None:
    """
    Requests and applies a new or existing License to a broker, Note that internet access is required on your
    computer

    More info on our docs page
    https://docs.remotivelabs.com/docs/remotive-broker/getting-started

    --connect describes how the connection is made to the broker and helps us properly connect to broker

    url      = Use url to connect to broker (use --url)
    hotspot  = If you are using RemotiveBox (our reference hardware) you can connect to the
               broker over its wifi hotspot. Licensing a broker on a RemotiveBox over its wifi hotspot
               requires you switch wi-fi network to the RemotiveBox hotspot called 'remotivelabs-xxx' where
               'xxx' is a random generated id.
               https://docs.remotivelabs.com/docs/remotive-broker/getting-started/remotive-box

    --url is the broker url, this is mandatory when connect type is "url"
    """

    license_flow = LicenseFlow()
    if connect == Connection.url:
        license_flow.request_with_url_with_internet(url)
    if connect == Connection.hotspot:
        license_flow.request_with_hotspot(url if url != "http://localhost:50051" else None)
