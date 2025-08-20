import dataclasses
from typing import Any

import requests

from cli.utils.rest_helper import RestHelper as Rest

#
# Attempt to start cloud-api.
# Might be better to generate somehow instead.
# Lets discuss further
#


@dataclasses.dataclass
class EmptyResponse:
    is_success: bool
    status_code: int


@dataclasses.dataclass
class JsonResponse:
    is_success: bool
    status_code: int
    __response: requests.Response

    def json(self) -> Any:
        return self.__response.json()

    def text(self) -> str:
        return self.__response.text


def __delete_response_from_response(response: requests.Response) -> EmptyResponse:
    if 200 > response.status_code > 299:
        ok = False
    else:
        ok = True
    return EmptyResponse(is_success=ok, status_code=response.status_code)


def __json_response_from_response(response: requests.Response) -> JsonResponse:
    if 200 > response.status_code > 299:
        ok = False
    else:
        ok = True
    return JsonResponse(is_success=ok, status_code=response.status_code, __response=response)


def create() -> JsonResponse:
    response = Rest.handle_post(url="/api/me/keys", return_response=True)
    return __json_response_from_response(response)


def revoke(name: str) -> EmptyResponse:
    res_revoke = Rest.handle_patch(f"/api/me/keys/{name}/revoke", quiet=True, allow_status_codes=[404, 401])
    return __delete_response_from_response(res_revoke)


def delete(name: str) -> EmptyResponse:
    res_delete = Rest.handle_delete(f"/api/me/keys/{name}", quiet=True, allow_status_codes=[404, 401])
    return __delete_response_from_response(res_delete)
