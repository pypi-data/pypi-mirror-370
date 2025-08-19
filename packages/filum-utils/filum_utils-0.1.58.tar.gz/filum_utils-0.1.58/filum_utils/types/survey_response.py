from typing import TypedDict, Dict, Any, Optional


class CreateSurveyResponse(TypedDict, total=False):
    identifier: str
    anonymous_id: str
    send_timestamp: str
    transaction_id: Optional[str]
    user_phone: Optional[str]
    user_email: Optional[str]
    user_name: Optional[str]
    user_id: Optional[str]
    source: Optional[str]
    triggered_source: Optional[str]
    sending_failed_reason: Optional[str]
    distribution_id: Optional[int]
    trigger_data: Optional[Dict[str, Any]]
    send_cost: Optional[float]
    zns_template_id: Optional[int]
    sms_template_id: Optional[int]
    brand_name: Optional[str]
    action_id: Optional[int]
    original_message_id: Optional[str]
    status: Optional[str]
