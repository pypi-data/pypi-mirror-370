from typing import TypedDict, Optional, Dict, Any

from filum_utils.types.account import Account


class _Context(TypedDict):
    id: str
    type: str


class AutomatedAction(TypedDict, total=False):
    id: int
    name: str
    run_type: str
    account: Account
    context: Optional[_Context]
    data: Optional[Dict[str, Any]]
    voucher_batch_id: Optional[int]
