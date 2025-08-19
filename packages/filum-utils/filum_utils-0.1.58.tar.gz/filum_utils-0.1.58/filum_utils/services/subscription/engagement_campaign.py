from datetime import date
from typing import Dict, Any, Optional

from filum_utils.clients.notification import RoutePath
from filum_utils.enums import ParentType
from filum_utils.services.subscription.base_campaign import BaseCampaignSubscriptionService
from filum_utils.types.action import Action
from filum_utils.types.engagement_campaign import EngagementCampaign
from filum_utils.types.organization import Organization
from filum_utils.types.subscription import Subscription


class EngagementCampaignSubscriptionService(BaseCampaignSubscriptionService):
    def __init__(
        self,
        engagement_campaign: EngagementCampaign,
        subscription: Subscription,
        action: Action,
        organization: Organization
    ):
        super().__init__(subscription, action, organization)
        self.campaign = engagement_campaign

    @property
    def parent(self):
        return self.campaign

    @property
    def member_account_id(self):
        account = self.campaign["account"] or {}
        return account.get("id")

    @property
    def run_type(self) -> str:
        return ""

    @property
    def _parent_id(self) -> str:
        return self.parent["id"]

    @property
    def _parent_name(self) -> str:
        return self.parent["name"]

    @property
    def _parent_type(self) -> str:
        return ParentType.ENGAGEMENT_CAMPAIGN

    @property
    def _notification_route(self) -> Dict[str, Any]:
        return {
            "path": RoutePath.ENGAGEMENT_CAMPAIGNS_DETAIL,
            "params": {
                "campaignId": self._parent_id
            }
        }

    def update_status(self, updated_status: str):
        self.filum_client.update_engagement_campaign_subscription_status(
            organization_id=self.organization["id"],
            campaign_id=self._parent_id,
            distribution_id=self.subscription_data.get("distribution_id"),
            updated_status=updated_status,
        )

    def _get_trigger_completed_notification_subtitle(
        self,
        channel_name: str,
        success_count: int
    ) -> str:
        return f"{success_count} message(s) sent via {channel_name}"

    @classmethod
    def has_limit_configuration(cls, campaign: EngagementCampaign, day: date) -> bool:
        daily_message_limit = campaign.get("daily_message_limit")
        if daily_message_limit is None:
            return False
        last_no_limit_day = cls._parse_date(campaign.get("last_no_limit_day"))
        return not last_no_limit_day or day != last_no_limit_day

    @classmethod
    def is_limit_reached(cls, campaign: EngagementCampaign, day: date) -> bool:
        if not cls.has_limit_configuration(campaign, day):
            return False
        last_limit_reached_day = cls._parse_date(campaign.get("last_limit_reached_day"))
        return bool(last_limit_reached_day and day == last_limit_reached_day)

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[date]:
        """Parse ISO format date string to date object."""
        return date.fromisoformat(date_str) if date_str else None
