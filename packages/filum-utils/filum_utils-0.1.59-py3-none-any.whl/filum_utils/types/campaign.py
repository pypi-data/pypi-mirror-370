from typing import TypedDict, Optional, Dict, Any

from filum_utils.types.account import Account
from filum_utils.types.survey import Survey


class Campaign(TypedDict, total=False):
    id: str
    name: str
    run_type: Optional[str]
    touchpoint_id: Optional[int]
    feedback_type: Optional[str]
    account: Account
    survey: Survey
    data: Optional[Dict[str, Any]]
    voucher_batch_id: Optional[int]
