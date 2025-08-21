from typing import Dict, Any, List, TypedDict, Optional

from filum_utils.clients.common import BaseClient
from filum_utils.clients.log import LogClient, LogType
from filum_utils.config import config
from filum_utils.enums import ObjectType
from filum_utils.types.mini_app import UpdateInstalledMiniApp


class InstalledMiniAppError(TypedDict):
    type: str
    message: Optional[str]
    sub_message: Optional[str]
    data: Any


class InstalledMiniAppsClient(BaseClient):
    def __init__(self):
        super().__init__(
            base_url=config.APPSTORE_BASE_URL,
            username=config.APPSTORE_USERNAME,
            password=config.APPSTORE_PASSWORD
        )

    def get_list(self, mini_app_ids: List[int] = None, page: int = 0, size: int = 100):
        data = self._request(
            method="GET",
            endpoint="/internal/installed-mini-apps",
            params={
                "page": page,
                "size": size,
                "mini_app_ids": mini_app_ids
            }
        )

        return data.get("items") or []


class InstalledMiniAppClient(BaseClient):
    def __init__(self, installed_mini_app_id: int = None, installed_mini_app: Dict[str, Any] = None):
        super().__init__(
            base_url=config.APPSTORE_BASE_URL,
            username=config.APPSTORE_USERNAME,
            password=config.APPSTORE_PASSWORD
        )

        if installed_mini_app:
            self.installed_mini_app = installed_mini_app
        else:
            self.installed_mini_app = self._request(
                method="GET",
                endpoint=f"/internal/installed-mini-apps/{installed_mini_app_id}"
            )

        self.log_client = LogClient()

    def get_data(self, key: str):
        data = self.installed_mini_app.get("data")
        return data and data.get(key)

    def get_service_account_info(self):
        return self.installed_mini_app and self.installed_mini_app.get("service_account_info")

    def update(self, updated_object: UpdateInstalledMiniApp):
        self.installed_mini_app = self._request(
            method="PUT",
            endpoint=f"/internal/installed-mini-apps/{self.installed_mini_app['id']}",
            data=updated_object
        )

    def update_data(self, updated_data: Dict[str, Any]):
        self.installed_mini_app = self._request(
            method="PUT",
            endpoint=f"/internal/installed-mini-apps/{self.installed_mini_app['id']}/data",
            data=updated_data
        )

    def handle_update_failed(
        self,
        error: InstalledMiniAppError,
        trigger_data: Optional[Dict[str, Any]] = None
    ):
        error_message = (
            error.get("message") or "An error occurred when updating installed mini app"
        )
        self._log(
            type=LogType.ERROR,
            code="400",
            title=error_message,
            subtitle=error.get("sub_message"),
            trigger_data=trigger_data,
            error_data=error["data"],
        )

    def _log(
        self,
        type: str,
        code: str,
        title: str,
        subtitle: str,
        trigger_data: Optional[Dict[str, Any]] = None,
        error_data: Optional[Dict[str, Any]] = None
    ):
        self.log_client.create_log(
            object_type=ObjectType.INSTALLED_MINI_APP,
            object_id=self.installed_mini_app["id"],
            type=type,
            code=code,
            title=title,
            subtitle=subtitle,
            trigger_data=trigger_data,
            error_data=error_data,
            member_organization_id=self.installed_mini_app.get("organization_id"),
        )
