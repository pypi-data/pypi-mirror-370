from typing import TypedDict, Optional, Dict, Any, List


class SurveyLogo(TypedDict, total=False):
    light_mode_url: Optional[str]
    dark_mode_url: Optional[str]


class Survey(TypedDict, total=False):
    id: int
    input_data: Optional[Dict[str, Any]]
    questions: Optional[List[Dict[str, Any]]]
    view_token: Optional[str]
    contact_form_enabled: Optional[bool]
    logo: Optional[SurveyLogo]
    translations: Optional[Dict[str, Any]]
    languages: Optional[List[Dict[str, Any]]]
