import re
from typing import Any, Dict, List, Optional

from filum_utils.enums import BaseEnum
from filum_utils.utils.datetime_formatter import DateTimeFormatter

PROPERTY_PLACEHOLDER_REGEX = r'\{{[^{}]*\}}'


class ZaloField:
    NAME = "name"
    TYPE = "type"
    REQUIRE = "require"
    ACCEPT_NULL = "acceptNull"
    MAX_LENGTH = "maxLength"


class ZaloVariableType(BaseEnum):
    URL = "PARAM_URL_ENCODE"
    DATE = "DATE"
    STRING = "STRING"


class BaseTemplate:
    @classmethod
    def clean_piped_text(cls, piped_text: str) -> Optional[str]:
        """
        Clean text by removing {{ and }} from the beginning and end.
        """
        if not piped_text:
            return None

        return piped_text.strip("{{").strip("}}").strip()

    @classmethod
    def _populate_object_data(
        cls,
        default_key: str,
        key_property_mappings: Dict[str, str],
        object_dict: Dict[str, Any],
    ) -> Any:
        """
        Get value from object dictionary based on property mapping.
        """
        property_name = key_property_mappings.get(default_key)
        value = None
        if property_name:
            value = object_dict.get(property_name)

        return value

    @staticmethod
    def _truncate_string(default_string: str, max_length: int = 30) -> str:
        """
        Truncate a string to a specified maximum length, adding "..." if truncated.
        """
        default_string = str(default_string)
        if len(default_string) < max_length:
            return default_string

        # max_length need to greater than 3 in order to have enough space for "..."
        if max_length > 3:
            max_length = max_length - 3
            formatted_string = default_string[:max_length]
            return f"{formatted_string}..."

        return default_string[:max_length]


class ContentTemplate(BaseTemplate):
    def __init__(self):
        super().__init__()

    def populate_object_data_to_str(
        self,
        default_string: str,
        piped_text_mappings: Dict[str, str],
        object_dict: Dict[str, Any],
    ):
        formatted_string = default_string

        variable_formats = re.findall(PROPERTY_PLACEHOLDER_REGEX, default_string) or []
        for variable_format in variable_formats:
            param_name: str = self.clean_piped_text(variable_format) or ""
            value = self._populate_object_data(
                default_key=param_name,
                key_property_mappings=piped_text_mappings,
                object_dict=object_dict
            )
            formatted_string = formatted_string.replace(variable_format, str(value))

        return formatted_string


class ZaloTemplate(BaseTemplate):
    def __init__(self):
        super().__init__()

    def populate_object_data_to_params(
        self,
        template_params: List[Dict[str, Any]],
        template_param_mappings: Dict[str, str],
        object_dict: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Populate object data for ZNS template with proper formatting.
        """
        data = {}
        for template_param in template_params:
            param_name = template_param[ZaloField.NAME] or ""
            value = self._populate_object_data(
                default_key=param_name,
                key_property_mappings=template_param_mappings,
                object_dict=object_dict
            )

            if value is None:
                data[param_name] = " "
                continue

            if template_param[ZaloField.TYPE] == ZaloVariableType.DATE:
                current_date = DateTimeFormatter.get_current_datetime()
                # format date for better display only
                date_string = str(value) if value else current_date.isoformat()
                value = DateTimeFormatter.format_to_dmy(date_string)

            value = " " if not value else value
            data[param_name] = self._truncate_string(
                default_string=value,
                max_length=template_param[ZaloField.MAX_LENGTH]
            )

        return data
