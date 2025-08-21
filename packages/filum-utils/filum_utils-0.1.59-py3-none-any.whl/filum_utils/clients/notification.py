from typing import Dict, TypedDict

from filum_utils.clients.common import BaseClient
from filum_utils.config import config
from filum_utils.enums import BaseEnum


class PublisherType(BaseEnum):
    DATA_CONNECTION = "Data Connection"
    VoC = "Voice of the Customer"
    AUTOMATED_ACTION = "Automated Action"


class RoutePath(BaseEnum):
    CONNECTIONS_DETAIL = "connectionsDetail"
    AUTOMATED_ACTIONS_DETAIL = "automatedActionsDetail"
    CAMPAIGNS_DETAIL = "listeningCampaignDetails"
    ENGAGEMENT_CAMPAIGNS_DETAIL = "engagementCampaignDetails"


class ErrorType:
    INTERNAL = "internal"
    EXTERNAL = "external"


class NotificationErrorMessage:
    INTERNAL = "Internal system error, please contact Filum for support"
    EXTERNAL = "Partner error, please contact Filum for support"


NOTIFICATION_ERROR_MESSAGE_MAPPINGS = {
    ErrorType.INTERNAL: NotificationErrorMessage.INTERNAL,
    ErrorType.EXTERNAL: NotificationErrorMessage.EXTERNAL,
}


class Route(TypedDict):
    path: str
    params: Dict[str, str]


class NotificationClient(BaseClient):
    def __init__(self):
        super().__init__(
            base_url=config.NOTIFICATION_BASE_URL,
            username=config.NOTIFICATION_USERNAME,
            password=config.NOTIFICATION_PASSWORD
        )

    def create_notification(
        self,
        publisher_type: str,
        title: str,
        subtitle: str,
        route: Route,
        member_account_id: int = None,
        member_organization_id: str = None,
    ):
        notification = {
            "title": title,
            "subtitle": subtitle,
            "publisher_type": publisher_type,
            "route": route,
            "member_account_id": member_account_id,
            "member_organization_id": member_organization_id
        }

        return self._request(
            method="POST",
            endpoint="/internal/notifications",
            data=notification
        )
