from typing import Dict, Any, Optional

from filum_utils.clients.notification import RoutePath
from filum_utils.enums import ParentType
from filum_utils.services.subscription.base_campaign import BaseCampaignSubscriptionService
from filum_utils.types.action import Action
from filum_utils.types.campaign import Campaign
from filum_utils.types.organization import Organization
from filum_utils.types.subscription import Subscription

Event = Optional[Dict[str, Any]]
User = Optional[Dict[str, Any]]


class CampaignSubscriptionService(BaseCampaignSubscriptionService):
    def __init__(
        self,
        campaign: Campaign,
        subscription: Subscription,
        action: Action,
        organization: Organization
    ):
        super().__init__(subscription, action, organization)
        self.campaign = campaign

    @property
    def parent(self):
        return self.campaign

    @property
    def member_account_id(self):
        account = self.campaign["account"] or {}
        return account.get("id")

    @property
    def run_type(self) -> Optional[str]:
        return self.campaign.get("run_type")

    @property
    def _parent_id(self) -> str:
        return self.parent["id"]

    @property
    def _parent_name(self) -> str:
        return self.parent["name"]

    @property
    def _parent_type(self) -> str:
        return ParentType.CAMPAIGN

    @property
    def _notification_route(self) -> Dict[str, Any]:
        return {
            "path": RoutePath.CAMPAIGNS_DETAIL,
            "params": {
                "campaignId": self._parent_id
            }
        }

    def update_status(self, updated_status: str):
        self.filum_client.update_campaign_subscription_status(
            campaign_id=self._parent_id,
            subscription_id=self.subscription_id,
            updated_status=updated_status,
        )

    def _get_trigger_completed_notification_subtitle(
        self,
        channel_name: str,
        success_count: int
    ) -> str:
        return f"{success_count} survey(s) sent via {channel_name}"
