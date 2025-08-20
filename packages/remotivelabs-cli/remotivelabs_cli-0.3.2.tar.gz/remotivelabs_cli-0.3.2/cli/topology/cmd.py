from __future__ import annotations

import typer

from cli.topology.start_trial import (
    MissingOrganizationError,
    NoActiveAccountError,
    NotAuthorizedError,
    NotAuthorizedToStartTrialError,
    NotSignedInError,
    SubscriptionExpiredError,
    start_trial,
)
from cli.typer import typer_utils
from cli.utils.console import print_generic_error, print_generic_message, print_hint

HELP = """
Manage RemotiveTopology resources
"""

app = typer_utils.create_typer(rich_markup_mode="rich", help=HELP)


@app.command("start-trial")
def start_trial_cmd(  # noqa: C901
    organization: str = typer.Option(None, help="Organization to start trial for", envvar="REMOTIVE_CLOUD_ORGANIZATION"),
) -> None:
    """
    Allows you ta start a 30 day trial subscription for running RemotiveTopology.

    You can read more at https://docs.remotivelabs.com/docs/remotive-topology.
    """
    try:
        subscription = start_trial(organization)
        if subscription.type == "trial":
            print_generic_message(f"topology trial active, expires {subscription.end_date}")
        elif subscription.type == "paid":
            print_generic_message(f"you already have a topology subscription, expires {subscription.end_date or 'Never'}")

    except NotSignedInError:
        print_generic_error(
            "You must first sign in to RemotiveCloud, please use [bold]remotive cloud auth login[/bold] to sign-in"
            "This requires a RemotiveCloud account, if you do not have an account you can sign-up at https://cloud.remotivelabs.com"
        )
        raise typer.Exit(2)

    except NoActiveAccountError:
        print_hint(
            "You have not actived your account, please run [bold]remotive cloud auth activate[/bold] to choose an account"
            "or [bold]remotive cloud auth login[/bold] to sign-in"
        )
        raise typer.Exit(3)

    except NotAuthorizedError:
        print_hint(
            "Your current active credentials are not valid, please run [bold]remotive cloud auth login[/bold] to sign-in again."
            "This requires a RemotiveCloud account, if you do not have an account you can sign-up at https://cloud.remotivelabs.com"
        )
        raise typer.Exit(4)

    except MissingOrganizationError:
        print_hint("You have not specified any organization and no default organization is set")
        raise typer.Exit(5)

    except NotAuthorizedToStartTrialError as e:
        print_generic_error(f"You are not allowed to start-trial topology in organization {e.organization}")
        raise typer.Exit(6)

    except SubscriptionExpiredError as e:
        if e.subscription.type == "trial":
            print_generic_error(f"Your Topology trial expired {e.subscription.end_date}, please contact support@remotivelabs.com")
            raise typer.Exit(7)

        print_generic_error(f"Your Topology subscription has expired {e.subscription.end_date}, please contact support@remotivelabs.com")
        raise typer.Exit(7)

    except Exception as e:
        print_generic_error(f"Unexpected error: {e}")
        raise typer.Exit(1)
