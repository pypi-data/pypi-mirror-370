from typing import List

from filum_utils.clients.common import BaseClient
from filum_utils.config import config
from filum_utils.types.segment import UserCustomProperty


class SegmentClient(BaseClient):
    def __init__(self, organization_id: str):
        super().__init__(
            base_url=config.SEGMENT_SERVICE_URL,
            username=config.SEGMENT_SERVICE_USERNAME,
            password=config.SEGMENT_SERVICE_PASSWORD
        )
        self.organization_id = organization_id

    def get_user_custom_property(
        self,
        filum_user_id: str,
        custom_property_name: str
    ):
        users = self.get_users_custom_properties(
            filum_user_ids=[filum_user_id],
            custom_property_names=[custom_property_name]
        )

        if not users:
            return None

        custom_properties = users[0].get("custom_properties") or {}
        return custom_properties.get(custom_property_name)

    def get_users_custom_properties(
        self,
        filum_user_ids: List[str],
        custom_property_names: List[str]
    ) -> List[UserCustomProperty]:
        return self._request(
            method="POST",
            endpoint="/find-users-prebuilt-custom-properties",
            params={"org_id": self.organization_id},
            data={
                "filum_users_ids": filum_user_ids,
                "custom_properties_names": custom_property_names,
            },
        )
