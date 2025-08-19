from typing import Any, Dict, TypedDict


class UserCustomProperty(TypedDict):
    filum_user_id: str
    custom_properties: Dict[str, Any]
