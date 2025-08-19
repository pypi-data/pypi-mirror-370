from filum_utils.clients.common import BaseClient
from filum_utils.config import config


class IAMClient(BaseClient):
    def __init__(
        self,
        base_url: str = config.IAM_BASE_URL,
        username: str = config.IAM_USERNAME,
        password: str = config.IAM_PASSWORD
    ):
        super().__init__(base_url, username, password)

    def get_organization(self, organization_id: str):
        return self._request(
            method="GET",
            endpoint=f"/internal/organizations/{organization_id}"
        )
