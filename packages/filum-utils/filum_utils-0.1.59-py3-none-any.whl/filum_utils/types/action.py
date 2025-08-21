from typing import TypedDict, Optional, Dict, Any


class ActionType(TypedDict, total=False):
    id: int
    internal_data: Optional[Dict[str, Any]]


class Action(TypedDict, total=False):
    id: int
    data: Optional[Dict[str, Any]]
    service_account_info: Optional[Any]
    action_type: ActionType
