from typing import Any, Dict, List, Optional, TypedDict

from filum_utils.enums import Period


class DataMapping(TypedDict, total=False):
    piped_text: str
    value: str
    value_type: Optional[str]


class TriggerData(TypedDict, total=False):
    segment_id: Optional[str]
    file_name: Optional[str]
    user_limit_per_trigger: Optional[int]
    data_mapping: Optional[List[DataMapping]]


class ZaloTemplateParam(TypedDict, total=False):
    name: str
    require: Optional[bool]  # based on ZNS template parameter name
    type: str
    maxLength: Optional[int]  # based on ZNS template parameter name
    minLength: Optional[int]  # based on ZNS template parameter name
    acceptNull: Optional[bool]  # based on ZNS template parameter name


class MetadataDetail(TypedDict, total=False):
    id: int
    name: str
    variable: str
    type: str


class MetadataMapping(TypedDict, total=False):
    property_name: str
    metadata_detail: MetadataDetail


class Target(TypedDict, total=False):
    metadata_value: str
    target_responses: int


class SmartDistributionConfig(TypedDict, total=False):
    period: Period
    response_rate: float
    metadata_id: int
    property_name: str
    targets: List[Target]


class SmartDistribution(TypedDict, total=False):
    enabled: bool
    config: SmartDistributionConfig


class SubscriptionData(TypedDict, total=False):
    input_data: Optional[Dict[str, Any]]
    last_current_index: Optional[
        int
    ]  # checking if last current index in request data is the same as the one in db
    last_current_row: Optional[
        int
    ]  # checking if last current row in request data is the same as the one in db
    triggered_source: Optional[str]
    trigger_data: Optional[TriggerData]
    distribution_id: Optional[str]
    purpose_id: Optional[str]
    segment_user_file_name: Optional[str]  # path to the user CSV stored in GCS
    metadata_mapping: Optional[
        List[MetadataMapping]
    ]  # maps segment properties to survey metadata fields
    smart_distribution: Optional[SmartDistribution]
    # for ZNS distribution
    zalo_template_id: Optional[str]
    zalo_template_params: Optional[List[ZaloTemplateParam]]
    zalo_template_param_mappings: Optional[Dict[str, str]]
    zns_template_id: Optional[int]
    # for SMS distribution
    sms_brand_name: Optional[str]
    sms_template_content: Optional[str]
    sms_template_without_accent: Optional[bool]
    sms_template_id: Optional[int]
    # for Messenger message distribution
    message: Optional[str]
    installed_source_id: Optional[int]


class MetadataGroup(TypedDict):
    value: str
    target_responses: int
    actual_responses: int
    gap: int
    estimated_send: int
    weighted_distribution: float
    max_send: int
    send_limit: int
    remaining_send: int
    total_users: int


class Subscription(TypedDict, total=False):
    id: str
    data: Optional[SubscriptionData]


class CallableResponse(TypedDict):
    success_count: int
    metadata_groups: Optional[Dict[str, MetadataGroup]]


class SmartDistributionParams(TypedDict):
    metadata_groups: Dict[str, MetadataGroup]
    user_metadata_property_name: str
