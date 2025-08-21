import datetime
import logging
from enum import Enum
from typing import Optional, Union

from dateutil import parser
from dateutil.tz import gettz

from filum_utils.errors import BaseError, ErrorMessage


class DateFormatOrder(str, Enum):
    YEAR_FIRST = "year_first"
    DAY_FIRST = "day_first"


class DateTimeFormatter:
    """A class to handle datetime formatting operations with Vietnam timezone"""

    VIETNAM_TIMEZONE = "Asia/Ho_Chi_Minh"

    @classmethod
    def get_vietnam_tz(cls) -> datetime.tzinfo:
        """Get Vietnam timezone object"""
        tz = gettz(cls.VIETNAM_TIMEZONE)
        if tz is None:
            raise BaseError(ErrorMessage.TIMEZONE_ERROR)
        return tz

    @classmethod
    def get_current_datetime(cls) -> datetime.datetime:
        """Get current datetime in Vietnam timezone"""
        return datetime.datetime.now(tz=cls.get_vietnam_tz())

    @classmethod
    def get_current_date(cls) -> datetime.date:
        """Get current date in Vietnam timezone"""
        return cls.get_current_datetime().date()

    @classmethod
    def get_current_datetime_str(cls) -> str:
        """Get current datetime as string"""
        return str(cls.get_current_datetime())

    @classmethod
    def timestamp_to_datetime(
        cls,
        timestamp: Union[int, float, str, None],
        is_milliseconds: bool = True
    ) -> Optional[datetime.datetime]:
        """Convert timestamp to datetime object

        Args:
            timestamp: Unix timestamp in milliseconds or seconds
            is_milliseconds: True if timestamp is in milliseconds, False if in seconds

        Returns:
            datetime object in Vietnam timezone or None if timestamp is empty
        """
        if not timestamp:
            return None

        timestamp_float = float(timestamp)
        timestamp_float = timestamp_float / 1000 if is_milliseconds else timestamp_float

        return datetime.datetime.fromtimestamp(
            timestamp_float,
            tz=cls.get_vietnam_tz()
        )

    @classmethod
    def timestamp_to_datetime_str(
        cls,
        timestamp: Union[int, float, str, None],
        is_milliseconds: bool = True
    ) -> Optional[str]:
        """Convert timestamp to datetime string"""
        formatted_datetime = cls.timestamp_to_datetime(timestamp, is_milliseconds)
        return str(formatted_datetime) if formatted_datetime else None

    @classmethod
    def format_to_dmy(cls, datetime_str: Optional[str]) -> Optional[str]:
        """Convert datetime/date string to dd/mm/yyyy format
        
        Args:
            datetime_str: Input datetime or date string
            
        Returns:
            Date string in dd/mm/yyyy format (e.g., "31/12/2023") or None if input is empty
            
        Raises:
            BaseError: If string cannot be formatted
        """
        if not datetime_str:
            return None

        parsed_datetime = cls.str_to_datetime(datetime_str)
        if not parsed_datetime:
            raise BaseError(
                message=ErrorMessage.INVALID_DATETIME_STRING,
                data={"datetime_str": datetime_str}
            )

        return parsed_datetime.strftime("%d/%m/%Y")

    @classmethod
    def get_days_ago_datetime(cls, days_ago: int) -> datetime.datetime:
        """Get datetime object for specified days ago"""
        return cls.get_current_datetime() - datetime.timedelta(days=days_ago)

    @classmethod
    def get_days_ago_datetime_str(cls, days_ago: int) -> str:
        """Get datetime string for specified days ago"""
        days_ago_datetime = cls.get_days_ago_datetime(days_ago)
        return str(days_ago_datetime)

    @classmethod
    def str_to_datetime(cls, datetime_str: str) -> Optional[datetime.datetime]:
        """Convert string to datetime object with automatic format detection
        
        Handles various datetime string formats and converts them to datetime objects
        with Vietnam timezone. Supports both date-first (dd-mm-yyyy) and 
        year-first (yyyy-mm-dd) formats.
        
        Args:
            datetime_str: Input datetime string (e.g., "2023-12-31 15:30:00" or "31-12-2023 15:30:00")
            
        Returns:
            datetime object in Vietnam timezone or None if parsing fails
        """
        if not datetime_str:
            return None

        normalized_datetime_str = cls._normalize_datetime_format(datetime_str)
        datetime_str_with_timezone = cls._add_timezone(normalized_datetime_str)

        date_part = datetime_str_with_timezone.split("T")[0]
        format_order = cls._detect_date_format(date_part)

        if not format_order:
            logging.error(f"Unable to detect date format in string: {datetime_str}")
            return None

        return cls._parse_to_datetime(
            datetime_str_with_timezone,
            is_day_first=(format_order == DateFormatOrder.DAY_FIRST)
        )

    @staticmethod
    def _normalize_datetime_format(datetime_str: str) -> str:
        """Standardize datetime string format
        
        Converts various datetime string formats to a standard format:
        - Replaces spaces with 'T' for ISO format
        - Converts forward slashes to hyphens for consistent parsing
        """
        return datetime_str.replace(" ", "T").replace("/", "-")

    @classmethod
    def _add_timezone(cls, datetime_str: str) -> str:
        """Add Vietnam timezone (+07:00) to datetime string if missing
        
        Handles various cases:
        - Strings ending with 'Z' (UTC)
        - Strings without timezone
        - Strings with existing timezone
        """
        if not datetime_str:
            return datetime_str

        # Handle UTC timezone 
        if datetime_str.endswith("Z"):
            datetime_str = datetime_str.replace("Z", "")
            return f"{datetime_str}+00:00"

        # Check if string contains time part
        parts = datetime_str.split("T")
        if len(parts) != 2:
            return datetime_str

        # Add timezone if missing
        time_part = parts[1]
        return datetime_str if "+" in time_part else f"{datetime_str}+07:00"

    @staticmethod
    def _detect_date_format(date_str: str) -> Optional[DateFormatOrder]:
        """Detect whether date string is in year-first or day-first format
        
        Attempts to parse the date string in both formats:
        - yyyy-mm-dd (year first)
        - dd-mm-yyyy (day first)
        
        Returns:
            DateFormatOrder enum indicating detected format or None if format is invalid
        """
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return DateFormatOrder.YEAR_FIRST
        except ValueError:
            pass

        try:
            datetime.datetime.strptime(date_str, "%d-%m-%Y")
            return DateFormatOrder.DAY_FIRST
        except ValueError:
            return None

    @classmethod
    def _parse_to_datetime(
        cls,
        datetime_str: str,
        is_day_first: bool = False
    ) -> Optional[datetime.datetime]:
        """Parse datetime string using detected format
        
        Args:
            datetime_str: Normalized datetime string with timezone
            is_day_first: True if date is in dd-mm-yyyy format, False for yyyy-mm-dd
            
        Returns:
            datetime object in Vietnam timezone or None if parsing fails
        """
        if not datetime_str:
            return None

        return parser.parse(
            datetime_str,
            dayfirst=is_day_first,
            yearfirst=not is_day_first
        ).astimezone(tz=cls.get_vietnam_tz())
