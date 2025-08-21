import json
from typing import Dict, TypedDict, Any, Optional

from filum_utils.clients.common import BaseClient
from filum_utils.config import config


class LogType:
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class StatusCode:
    SYNC_SUCCESS = "DC101"
    SYNC_WARNING = "DC200"
    SYNC_ERROR = "DC403"
    SETUP_ERROR = "DC402"


class Route(TypedDict):
    path: str
    params: Dict[str, str]


class LogClient(BaseClient):
    def __init__(self):
        super().__init__(
            base_url=config.NOTIFICATION_BASE_URL,
            username=config.NOTIFICATION_USERNAME,
            password=config.NOTIFICATION_PASSWORD
        )

    def create_log(
        self,
        object_type: str,
        object_id: str,
        type: str,
        code: str,
        title: str,
        subtitle: str,
        parent_type: str = None,
        parent_id: str = None,
        error_data: Optional[Dict[str, Any]] = None,
        trigger_data: Optional[Dict[str, Any]] = None,
        member_account_id: str = None,
        member_organization_id: str = None,
    ):
        data = {}
        if error_data:
            data["error_data"] = error_data

        if trigger_data:
            data["trigger_data"] = trigger_data

        data = self._to_string(data)
        log = {
            "type": type,
            "code": code,
            "title": title,
            "subtitle": subtitle,
            "data": data,
            "object_type": object_type,
            "object_id": object_id,
            "parent_type": parent_type,
            "parent_id": parent_id,
            "member_account_id": member_account_id,
            "member_organization_id": member_organization_id,
        }
        return self._request(
            method="POST",
            endpoint="/internal/logs",
            data=log
        )

    @staticmethod
    def _to_string(default_dict: Dict[str, Any]) -> str:
        return json.dumps(default_dict)
