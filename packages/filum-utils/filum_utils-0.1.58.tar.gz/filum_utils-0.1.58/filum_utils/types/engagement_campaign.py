from typing import TypedDict, Optional, Dict, Any

from filum_utils.types.account import Account


class EngagementCampaign(TypedDict, total=False):
    id: str
    name: str
    account: Account
    data: Optional[Dict[str, Any]]
    daily_message_limit: Optional[int]
    last_no_limit_day: Optional[str]  # ISO date
    last_limit_reached_day: Optional[str]  # ISO date
