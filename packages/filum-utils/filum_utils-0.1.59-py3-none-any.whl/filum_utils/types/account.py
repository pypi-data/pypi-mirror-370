from typing import Optional, TypedDict


class Account(TypedDict, total=False):
    id: str
    email: str
    full_name: Optional[str]
