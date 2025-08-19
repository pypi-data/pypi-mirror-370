from typing import Dict, List, TypedDict, Any, Optional

from filum_utils.config import config
from filum_utils.enums import ObjectType
from .common import BaseClient
from .log import LogClient, StatusCode, LogType
from .notification import NotificationClient, PublisherType, RoutePath, NOTIFICATION_ERROR_MESSAGE_MAPPINGS

VIOLATION_BATCH_SIZE = 2000


class InstalledSource(TypedDict):
    id: int
    access_token: Optional[str]
    data: Dict[str, Any]


class EventPropertyViolation(TypedDict):
    event_property_mapping_id: int
    error_code: str
    origin: str


class EventViolation(TypedDict):
    event_mapping_id: int
    installed_source_id: int
    violation_count: int
    processed_count: int
    event_property_violations: List[EventPropertyViolation]


class SyncResult(TypedDict):
    record_count: int
    error_count: int


class ConnectionError(TypedDict):
    type: str
    message: Optional[str]
    sub_message: Optional[str]
    data: Dict[str, Any]


class ConnectionsClient(BaseClient):
    def __init__(
        self,
        base_url=config.APPSTORE_BASE_URL,
        username=config.APPSTORE_USERNAME,
        password=config.APPSTORE_PASSWORD
    ):
        super().__init__(base_url, username, password)

    def get_connections(
        self,
        data_key: Optional[str] = None,
        data_value: Optional[str] = None,
        source_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        installed_mini_app_id: Optional[str] = None
    ):
        params = {}
        if data_key and data_value:
            params["data_key"] = data_key
            params["data_value"] = data_value

        if source_id:
            params["source_id"] = source_id

        if organization_id:
            params["organization_id"] = organization_id

        if installed_mini_app_id:
            params["installed_mini_app_id"] = installed_mini_app_id

        return self._request(
            method="GET",
            endpoint="/source/installed-sources",
            params=params,
        )


class ConnectionClient(BaseClient):
    def __init__(
        self,
        connection_id: int = None,
        connection=None,
        base_url=config.APPSTORE_BASE_URL,
        username=config.APPSTORE_USERNAME,
        password=config.APPSTORE_PASSWORD
    ):
        super().__init__(base_url, username, password)
        if not connection:
            self.connection = self._request(
                method="GET",
                endpoint=f"/source/installed-sources/{connection_id}",
            )
        else:
            self.connection = connection
        self.log_client = LogClient()
        self.notification_client = NotificationClient()

    def get_access_token(self):
        return self.connection and self.connection.get("access_token")

    def get_webhook_url(self):
        return self.connection and self.connection.get("webhook_endpoint_url")

    def get_service_account_info(self):
        return self.connection and self.connection.get("service_account_info")

    def get_data(self, key: str):
        data = self.connection.get("data")
        return data and data.get(key)

    def update_data(self, updated_data: Dict[str, Any]):
        self._request(
            method="PUT",
            endpoint=f"/source/installed-sources/{self.connection['id']}/data",
            data=updated_data
        )

    def update_status(self, status: str):
        self._request(
            method="PUT",
            endpoint=f"/source/installed-sources/{self.connection['id']}/status",
            data={
                "status": status
            }
        )

    def get_event_mappings(self):
        return self._request(
            method="GET",
            endpoint=f"/source/installed-sources/{self.connection['id']}/event-mappings/all",
        )

    def update_event_mapping_data(self, event_mapping_id, updated_data: Dict[str, Any]):
        self._request(
            method="PUT",
            endpoint=f"/source/event-mappings/{event_mapping_id}/data",
            data=updated_data,
        )

    def sync(self):
        self._request(
            method="POST",
            endpoint=f"/source/installed-sources/{self.connection['id']}/sync",
        )

    def create_event_violations(self, violations: List[EventViolation]):
        if not violations:
            return
        self._request(
            method="POST",
            endpoint=f"/source/installed-sources/{self.connection['id']}/event-violation-batch",
            data=violations,
        )

    def create_event_property_violations(self, violations: List[EventPropertyViolation]):
        if not violations:
            return
        if len(violations) <= VIOLATION_BATCH_SIZE:
            self._request(
                method="POST",
                endpoint=f"/source/event-property-violation-batch",
                data=violations,
            )
            return
        start_index = 0
        while start_index < len(violations):
            end_index = start_index + VIOLATION_BATCH_SIZE
            self._request(
                method="POST",
                endpoint=f"/source/event-property-violation-batch",
                data=violations[start_index:end_index],
            )
            start_index = end_index

    def handle_sync_finished(self, result: SyncResult, notify: bool = False):
        record_count = result["record_count"]
        error_count = result["error_count"]
        if error_count > 0:
            log_type = LogType.WARNING
            status_code = StatusCode.SYNC_WARNING
            title = "Your data has been processed with violations. Please check the Violations tab for details."
            subtitle = f"{record_count} data record(s) processed. {error_count} warning(s)."
        else:
            log_type = LogType.INFO
            status_code = StatusCode.SYNC_SUCCESS
            title = "Your data has been processed successfully."
            subtitle = f"{record_count} data record(s) processed."

        self._log(
            type=log_type,
            code=status_code,
            title=title,
            subtitle=subtitle,
        )

        if notify:
            self._notify(
                title=f"{self.connection['name']} has finished importing data",
                subtitle=subtitle,
            )

    def handle_sync_failed(
        self,
        error: ConnectionError,
        trigger_data: Optional[Dict[str, Any]] = None,
        notify: bool = False
    ):
        error_message = (
            error.get("message") or "An error occurred when processing your data, please contact Filum for support."
        )
        self._log(
            type=LogType.ERROR,
            code=StatusCode.SYNC_ERROR,
            title=error_message,
            subtitle=error.get("sub_message"),
            trigger_data=trigger_data,
            error_data=error["data"],
        )

        if notify:
            self._notify(
                title=f"{self.connection.get('name')} has error",
                subtitle=NOTIFICATION_ERROR_MESSAGE_MAPPINGS[error["type"]],
            )

    def handle_setup_failed(
        self,
        error: ConnectionError,
        trigger_data: Optional[Dict[str, Any]] = None,
        notify: bool = False
    ):
        error_message = (
            error.get("message") or "An error occurred when setup your source, please contact Filum for support."
        )
        self._log(
            type=LogType.ERROR,
            code=StatusCode.SETUP_ERROR,
            title=error_message,
            subtitle=error.get("sub_message"),
            trigger_data=trigger_data,
            error_data=error["data"],
        )

        if notify:
            self._notify(
                title=f"{self.connection.get('name')} has error",
                subtitle=NOTIFICATION_ERROR_MESSAGE_MAPPINGS[error["type"]],
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
            object_type=ObjectType.INSTALLED_SOURCE,
            object_id=self.connection["id"],
            type=type,
            code=code,
            title=title,
            subtitle=subtitle,
            trigger_data=trigger_data,
            error_data=error_data,
            member_account_id=self.connection.get("member_account_id"),
            member_organization_id=self.connection.get("organization_id"),
        )

    def _notify(self, title: str, subtitle: str):
        self.notification_client.create_notification(
            publisher_type=PublisherType.DATA_CONNECTION,
            title=title,
            subtitle=subtitle,
            route=self._get_log_route(),
            member_account_id=self.connection.get("member_account_id"),
            member_organization_id=self.connection.get("organization_id"),
        )

    def _get_log_route(self):
        return {
            "path": RoutePath.CONNECTIONS_DETAIL,
            "params": {
                "connectionId": self.connection["id"],
                "tab": "logs"
            }
        }
