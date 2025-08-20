from __future__ import annotations

import datetime
from dataclasses import dataclass
from datetime import date
from typing import Any

from cli.settings import settings
from cli.settings.config_file import Account
from cli.utils.rest_helper import RestHelper
from cli.utils.time import parse_date


class NoActiveAccountError(Exception):
    """Raised when the user has no active account, but there are available accounts to activate"""


class NotSignedInError(Exception):
    """Raised when the user has no active account, and no available accounts to activate"""


class NotAuthorizedError(Exception):
    """Raised when the user is not authorized"""

    def __init__(self, account: Account):
        self.account = account


class MissingOrganizationError(Exception):
    """Raised when the user has not specified an organization and no default organization is set"""


class NotAuthorizedToStartTrialError(Exception):
    """Raised when the user is not authorized to start a topology trial"""

    def __init__(self, account: Account, organization: str):
        self.account = account
        self.organization = organization


class SubscriptionExpiredError(Exception):
    """Raised when the subscription has expired"""

    def __init__(self, subscription: Subscription):
        self.subscription = subscription


@dataclass
class Subscription:
    type: str
    display_name: str
    feature: str
    start_date: date
    end_date: date

    @staticmethod
    def from_dict(data: Any) -> Subscription:
        if not isinstance(data, dict):
            raise ValueError(f"Invalid subscription data {data}")

        return Subscription(
            type=data["subscriptionType"],
            display_name=data["displayName"],
            feature=data["feature"],
            start_date=parse_date(data["startDate"]),
            end_date=parse_date(data["endDate"]),
        )


def start_trial(organization: str | None = None) -> Subscription:
    """
    Start a 30 day trial subscription for running RemotiveTopology.

    # TODO: move authentication (and basic authorization) to a logged_in decorator
    """
    active_account = settings.get_active_account()
    active_token_file = settings.get_active_token_file()

    if not active_account or not active_token_file:
        if len(settings.list_accounts()) == 0:
            raise NotSignedInError()
        raise NoActiveAccountError()

    if not RestHelper.has_access("/api/whoami"):
        raise NotAuthorizedError(account=active_account)

    valid_org = organization or active_account.default_organization
    if not valid_org:
        raise MissingOrganizationError()

    res = RestHelper.handle_get(f"/api/bu/{valid_org}/features/topology", return_response=True, allow_status_codes=[403, 404])
    if res.status_code == 403:
        raise NotAuthorizedToStartTrialError(account=active_account, organization=valid_org)
    if res.status_code == 404:
        created = RestHelper.handle_post(f"/api/bu/{valid_org}/features/topology", return_response=True)
        subscription = Subscription.from_dict(created.json())
    else:
        # 200 OK means we already have a valid subscription
        subscription = Subscription.from_dict(res.json())

    # check subscription validity
    if subscription.end_date < datetime.datetime.now().date():
        raise SubscriptionExpiredError(subscription=subscription)

    return subscription
