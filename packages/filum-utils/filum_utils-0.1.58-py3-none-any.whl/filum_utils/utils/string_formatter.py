import re
from typing import Optional


class StringFormatter:
    @classmethod
    def remove_accent_vietnamese(cls, s: str) -> str:
        s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
        s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
        s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
        s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
        s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
        s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
        s = re.sub(r'[ìíịỉĩ]', 'i', s)
        s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
        s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
        s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
        s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
        s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
        s = re.sub(r'[đ]', 'd', s)
        s = re.sub(r'[Đ]', 'D', s)
        return s

    @classmethod
    def transform_phone(cls, phone: Optional[str]) -> Optional[str]:
        if phone == "None":
            phone = None

        if not phone:
            return None

        if phone.startswith("0"):
            return cls._format_phone(phone, "0", True)

        if phone.startswith("+"):
            return cls._format_phone(phone, "+", False)

        return phone

    @classmethod
    def _format_phone(cls, phone: str, removed_str: str, is_formatted: bool = False) -> str:
        array_phone = phone.split(removed_str, 1)
        formatted_phone = array_phone[1]
        if is_formatted:
            formatted_phone = "84" + formatted_phone

        return formatted_phone
