from __future__ import annotations

import os

import typer
from trogon import Trogon
from typer.main import get_group

from cli.broker import app as broker_app
from cli.cloud import app as cloud_app
from cli.connect.connect import app as connect_app
from cli.settings import Settings, settings
from cli.settings.migration.migrate_all_token_files import migrate_any_legacy_tokens
from cli.settings.migration.migrate_config_file import migrate_config_file
from cli.settings.migration.migrate_legacy_dirs import migrate_legacy_settings_dirs
from cli.tools.tools import app as tools_app
from cli.topology.cmd import app as topology_app
from cli.typer import typer_utils
from cli.utils import versions
from cli.utils.console import print_generic_error, print_generic_message


def is_featue_flag_enabled(env_var: str) -> bool:
    """Check if an environment variable indicates a feature is enabled."""
    return os.getenv(env_var, "").lower() in ("true", "1", "yes", "on")


if os.getenv("GRPC_VERBOSITY") is None:
    os.environ["GRPC_VERBOSITY"] = "NONE"

app = typer_utils.create_typer(
    rich_markup_mode="rich",
    help="""
Welcome to RemotiveLabs CLI - Simplify and automate tasks for cloud resources and brokers

For documentation - https://docs.remotivelabs.com
""",
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"remotivelabs-cli {versions.cli_version()} ({versions.platform_info()})")


def test_callback(value: int) -> None:
    if value:
        print_generic_message(str(value))
        raise typer.Exit()


def check_for_newer_version(settings: Settings) -> None:
    versions.check_for_update(settings)


def run_migrations(settings: Settings) -> None:
    """
    Run all migration scripts.

    Each migration script is responsible for a particular migration, and order matters.
    """
    # 1. Migrate legacy settings dirs
    migrate_legacy_settings_dirs(settings.config_dir)

    # 2. Migrate any legacy tokens
    has_migrated_tokens = migrate_any_legacy_tokens(settings)

    # 3. Migrate legacy config file format
    migrate_config_file(settings.config_file_path, settings)

    if has_migrated_tokens:
        print_generic_error("Migrated old credentials and configuration files, you may need to login again or activate correct credentials")


def set_default_org_as_env(settings: Settings) -> None:
    """
    If not already set, take the default organisation from file and set as env
    This has to be done early before it is read
    """
    if "REMOTIVE_CLOUD_ORGANIZATION" not in os.environ:
        active_account = settings.get_active_account()
        if active_account and active_account.default_organization:
            os.environ["REMOTIVE_CLOUD_ORGANIZATION"] = active_account.default_organization


@app.callback()
def main(
    _the_version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Print current version",
    ),
) -> None:
    run_migrations(settings)
    check_for_newer_version(settings)
    set_default_org_as_env(settings)
    # Do other global stuff, handle other global options here


@app.command()
def tui(ctx: typer.Context) -> None:
    """
    Explore remotive-cli and generate commands with this textual user interface application
    """

    Trogon(get_group(app), click_context=ctx).run()


app.add_typer(broker_app, name="broker", help="Manage a single broker - local or cloud")
app.add_typer(cloud_app, name="cloud", help="Manage resources in RemotiveCloud")
app.add_typer(connect_app, name="connect", help="Integrations with other systems")
app.add_typer(tools_app, name="tools")
app.add_typer(
    topology_app,
    name="topology",
    help="""
Interact and manage RemotiveTopology resources

Read more at https://docs.remotivelabs.com/docs/remotive-topology
""",
)
