import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Type, Union

from filum_utils.utils.automated_action.enums import (
    CampaignProperty,
    ConversationProperty,
    ObjectName,
    PROPERTY_PLACEHOLDER_REGEX,
    SegmentProperty,
    SurveyAnsweredEventProperty,
    SurveyResponseProperty,
    TRANSLATION_FORMAT_REGEX,
    UserProperty,
    VariableProperty
)
from filum_utils.enums import ActionMetaDataKey

SEGMENT_DETAIL_BASE_URL = "/customers/segments"
CAMPAIGN_DETAIL_BASE_URL = "/listening/campaigns"
USER_DETAIL_BASE_URL = "/customers/profile"
SURVEY_RESPONSE_BASE_URL = "/inbox/responses"
CONVERSATION_BASE_URL = "/conversations"

class AutomatedActionStringFormatter:
    @classmethod
    def populate_data(
        cls,
        default_string: str,
        event: Dict[str, Any] = None,
        user: Dict[str, Any] = None,
        campaign: Dict[str, Any] = None,
        segment: Dict[str, Any] = None,
        survey_response: Dict[str, Any] = None,
        conversation: Dict[str, Any] = None,
        platform_url: str = None,
        action: Dict[str, Any] = None,
    ) -> str:
        if not default_string:
            return default_string

        if platform_url:
            platform_url = platform_url.rstrip("/")

        formatted_string = default_string
        populate_data_factory = PopulateDataFactory(
            event=event,
            user=user,
            campaign=campaign,
            segment=segment,
            survey_response=survey_response,
            conversation=conversation,
        )

        for variable_format in re.findall(PROPERTY_PLACEHOLDER_REGEX, default_string):
            object_name, property_name = cls._destructure_variable(
                variable_format=variable_format,
            )

            value = populate_data_factory.populate_data(
                property_name=property_name,
                object_name=object_name,
                platform_url=platform_url,
                action=action,
            )
            value = "" if value is None else value
            formatted_string = formatted_string.replace(variable_format, str(value))

        return formatted_string

    @classmethod
    def translate_str(
        cls,
        default_str: Union[str, None],
        translation: Union[Dict[str, Any], None] = None
    ) -> Union[str, None]:
        formatted_str = default_str
        if not default_str:
            return formatted_str

        if not translation:
            return formatted_str

        for translation_format in re.findall(pattern=TRANSLATION_FORMAT_REGEX, string=default_str):
            translated_value = translation.get(translation_format) or ""
            formatted_str = formatted_str.replace(translation_format, translated_value)

        return formatted_str

    @staticmethod
    def _destructure_variable(variable_format: str) -> Tuple[Optional[str], Optional[str]]:
        variable_name = variable_format.strip("{{").strip("}}")
        if not variable_name:
            return None, None

        variable_parts = variable_name.split(".")

        object_name = variable_parts[0].strip()
        property_name_parts = variable_parts[1:]

        property_name = " ".join([part.strip() for part in property_name_parts])
        property_name = property_name.replace("_", " ")

        return object_name, property_name



class AbstractPopulateData(ABC):
    @abstractmethod
    def populate_data(
        self,
        property_name: str,
        data: Dict[str, Any],
        platform_url: str = None,
        action: Dict[str, Any] = None,
    ) -> Optional[Any]:
        ...


class EventPopulateData(AbstractPopulateData):
    @classmethod
    def get_mapping_value(cls, action: Dict[str, Any], property_name: str, property_value: Any) -> Any:
        if not action or not property_value:
            return property_value

        action_data = action.get("data") or {}
        property_value_mappings = action_data.get(ActionMetaDataKey.PROPERTY_VALUE_MAPPINGS) or {}
        if not property_value_mappings:
            return property_value

        value_mappings = property_value_mappings.get(property_name) or {}
        if not value_mappings:
            return property_value

        return value_mappings.get(str(property_value)) or property_value

    def populate_data(
        self,
        property_name: str,
        data: Dict[str, Any],
        platform_url: str = None,
        action: Dict[str, Any] = None,
    ) -> Optional[Any]:
        if not data:
            return None

        value = data.get(property_name)
        if property_name == SurveyAnsweredEventProperty.METRIC_TYPE:
            value = value.upper() if value else None

        if not value and property_name == VariableProperty.TEXT:
            value = data.get(SurveyAnsweredEventProperty.TEXT)

        return self.get_mapping_value(action, property_name, value)


class UserPopulateData(AbstractPopulateData):
    @classmethod
    def _generate_user_link(
        cls,
        platform_url: str,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> str:
        default_link = f"{platform_url}{USER_DETAIL_BASE_URL}"
        if not phone and not email:
            return ""

        if phone:
            return f"{default_link}/redirect?Phone={phone}"

        return f"{default_link}/redirect?Email={email}"

    def populate_data(
        self,
        property_name: str,
        data: Dict[str, Any],
        platform_url: str = None,
        action: Dict[str, Any] = None,
    ) -> Optional[Any]:
        if not data:
            return None

        if property_name == VariableProperty.ID:
            property_name = UserProperty.ID

        user_phone = data.get(UserProperty.PHONE)
        user_email = data.get(UserProperty.EMAIL)
        if property_name == VariableProperty.LINK:
            return self._generate_user_link(platform_url, user_phone, user_email)

        if not property_name:
            user_name = data.get(UserProperty.NAME)
            user_data = user_phone or user_email
            if not user_name:
                return user_data

            return f"{user_name} - {user_data}" if user_data else user_name

        return data.get(property_name)


class SegmentPopulateData(AbstractPopulateData):
    def populate_data(
        self,
        property_name: str,
        data: Dict[str, Any],
        platform_url: str = None,
        action: Dict[str, Any] = None,
    ) -> Optional[Any]:
        if not data:
            return None

        if property_name == VariableProperty.NAME:
            return data.get(SegmentProperty.NAME)

        if property_name == VariableProperty.SIZE:
            return data.get(SegmentProperty.TOTAL_USERS) or 0

        if property_name == VariableProperty.LINK:
            segment_id = data.get(SegmentProperty.ID)
            return f"{platform_url}{SEGMENT_DETAIL_BASE_URL}/{segment_id}"

        return None


class CampaignPopulateData(AbstractPopulateData):
    def populate_data(
        self,
        property_name: str,
        data: Dict[str, Any],
        platform_url: str = None,
        action: Dict[str, Any] = None,
    ) -> Optional[Any]:
        if not data:
            return None

        if property_name == VariableProperty.NAME:
            return data.get(CampaignProperty.NAME)

        campaign_id = data.get(CampaignProperty.ID)
        if property_name == VariableProperty.ID:
            return campaign_id

        if campaign_id and property_name == VariableProperty.LINK:
            return f"{platform_url}{CAMPAIGN_DETAIL_BASE_URL}/{campaign_id}"

        return None


class SurveyResponsePopulateData(AbstractPopulateData):
    def populate_data(
        self,
        property_name: str,
        data: Dict[str, Any],
        platform_url: str = None,
        action: Dict[str, Any] = None,
    ) -> Optional[Any]:
        if not data:
            return None

        response_id = data.get(SurveyResponseProperty.ID)
        if property_name == VariableProperty.ID:
            return response_id

        if response_id and property_name == VariableProperty.LINK:
            return f"{platform_url}{SURVEY_RESPONSE_BASE_URL}/{response_id}"

        return None


class ConversationPopulateData(AbstractPopulateData):
    def populate_data(
        self,
        property_name: str,
        data: Dict[str, Any],
        platform_url: str = None,
        action: Dict[str, Any] = None,
    ) -> Optional[Any]:
        if not data:
            return None

        conversation_id = data.get(ConversationProperty.ID)
        if property_name == VariableProperty.ID:
            return conversation_id

        if conversation_id and property_name == VariableProperty.LINK:
            return f"{platform_url}{CONVERSATION_BASE_URL}/{conversation_id}"

        return None


class PopulateDataFactory:
    POPULATE_SERVICE_CLASS_MAPPINGS: Dict[str, Type[AbstractPopulateData]] = {
        ObjectName.EVENT: EventPopulateData,
        ObjectName.USER: UserPopulateData,
        ObjectName.SEGMENT: SegmentPopulateData,
        ObjectName.CAMPAIGN: CampaignPopulateData,
        ObjectName.SURVEY_RESPONSE: SurveyResponsePopulateData,
        ObjectName.CONVERSATION: ConversationPopulateData,
    }

    def __init__(
        self,
        event: Optional[Dict[str, Any]] = None,
        user: Optional[Dict[str, Any]] = None,
        campaign: Optional[Dict[str, Any]] = None,
        segment: Optional[Dict[str, Any]] = None,
        survey_response: Optional[Dict[str, Any]] = None,
        conversation: Optional[Dict[str, Any]] = None,
    ):
        self._object_data_mappings = {
            ObjectName.EVENT: event,
            ObjectName.USER: user,
            ObjectName.CAMPAIGN: campaign,
            ObjectName.SEGMENT: segment,
            ObjectName.SURVEY_RESPONSE: survey_response,
            ObjectName.CONVERSATION: conversation,
        }

    def populate_data(
        self,
        object_name,
        property_name: str,
        platform_url: str = None,
        action: Dict[str, Any] = None,
    ) -> Optional[Any]:
        POPULATE_SERVICE_CLASS = self.POPULATE_SERVICE_CLASS_MAPPINGS.get(object_name)
        if not POPULATE_SERVICE_CLASS:
            return None

        object_data = self._object_data_mappings.get(object_name)
        if not object_data:
            return None

        return POPULATE_SERVICE_CLASS().populate_data(
            property_name=property_name,
            data=object_data,
            platform_url=platform_url,
            action=action,
        )
