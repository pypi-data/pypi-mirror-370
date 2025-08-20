from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Optional

from pydantic import BaseModel

from cli.utils.time import parse_datetime


class StateFile(BaseModel):
    """
    Contains CLI state and other application specific data.
    """

    version: str = "1.0"
    last_update_check_time: Optional[str] = None

    def should_perform_update_check(self) -> bool:
        """
        Check if we should perform an update check.

        Returns True if the last update check time is older than 2 hours.

        For Docker environments, returns False and sets a backdated timestamp
        to prevent constant update checks due to ephemeral disks.
        """
        if not self.last_update_check_time:
            if os.environ.get("RUNS_IN_DOCKER"):
                # To prevent that we always check update in docker due to ephemeral disks we write an "old" check if the state
                # is missing. If no disk is mounted we will never get the update check but if its mounted properly we will get
                # it on the second attempt. This is good enough
                self.last_update_check_time = (datetime.now() - timedelta(hours=10)).isoformat()
                return False
            return True  # Returning True will trigger a check, which will properly set last_update_check_time

        seconds = (datetime.now() - parse_datetime(self.last_update_check_time)).seconds
        return (seconds / 3600) > 2

    @classmethod
    def from_json_str(cls, data: str) -> StateFile:
        return cls.model_validate_json(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StateFile:
        return cls.model_validate(data)

    def to_json_str(self) -> str:
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


def loads(data: str) -> StateFile:
    """
    Creates a StateFile from a JSON string.
    """
    return StateFile.from_json_str(data)


def dumps(state: StateFile) -> str:
    """
    Returns the JSON string representation of the StateFile.
    """
    return state.to_json_str()
