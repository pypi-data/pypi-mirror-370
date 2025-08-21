from typing import Any, Dict, List, Optional, TypedDict

from filum_utils.clients.knowledge_base.enums import (
    KBDocumentColumnDataTypeEnum,
    KBDocumentColumnFilterTypeEnum,
    KBDocumentStatusEnum,
)


class UpsertDocumentChunkDataType(TypedDict):
    text: str
    categories: List[str]
    summary: str


class UpsertDocumentColumnSchemaDataType(TypedDict, total=False):
    column_name: str
    data_type: KBDocumentColumnDataTypeEnum
    filter_type: Optional[KBDocumentColumnFilterTypeEnum]
    unique_count: Optional[int]
    unique_values: Optional[List[str]]
    array_value_delimiter: Optional[str]
    is_primary_key: Optional[bool]


class UpsertDocumentDataType(TypedDict, total=False):
    document_id: str
    document_status: KBDocumentStatusEnum
    table_records: List[Dict[str, Any]]
    colum_schemas: List[UpsertDocumentColumnSchemaDataType]
    collection_name: str

    categories: Optional[List[str]]
