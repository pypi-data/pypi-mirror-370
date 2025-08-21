from typing import Any, Dict, List

from filum_utils.clients.common import BaseClient
from filum_utils.clients.knowledge_base.types import UpsertDocumentDataType
from filum_utils.config import config


class KnowledgeBaseClient(BaseClient):
    def __init__(self, organization_id: str):
        super().__init__(
            base_url=config.KNOWLEDGE_BASE_SERVICE_URL,
            username=config.KNOWLEDGE_BASE_SERVICE_USERNAME,
            password=config.KNOWLEDGE_BASE_SERVICE_PASSWORD,
        )
        self._organization_id = organization_id

    def upsert_documents(
        self, documents: List[UpsertDocumentDataType]
    ) -> Dict[str, Any]:
        return self._request(
            method="PUT",
            endpoint="/documents/from-records",
            params={"organization_id": self._organization_id},
            data={"documents": documents},
        )

    def delete_document(self, document_id: str):
        return self._request(
            method="DELETE",
            endpoint=f"/documents/{document_id}",
            params={"organization_id": self._organization_id},
        )
