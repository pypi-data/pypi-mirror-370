import json
import logging
from functools import wraps
from typing import Any, Dict, Optional

from sentry_sdk import capture_exception

from filum_utils.sentry import SentryClient



class ErrorType:
    INTERNAL = "internal"
    EXTERNAL = "external"

class ErrorMessage:
    IMPLEMENTATION_ERROR = "Implementation error"
    MISMATCH_LAST_CURRENT_INDEX = "Mismatch last current index"
    MISMATCH_SEGMENT_USER_FILE_NAME = "Mismatch segment user file name"
    MISSING_SEGMENT_ID = "Missing segment id"
    MISSING_FILE = "Missing file"
    INVALID_DATETIME_STRING = "Invalid datetime string format - unable to parse"
    TIMEZONE_ERROR = "Timezone error"
    MISSING_CONFIG_IN_SMART_DISTRIBUTION = "Missing config in smart distribution"
    MISSING_METADATA_GROUPS_TO_PUBLISH_SUBSCRIPTION = "Missing metadata groups to publish subscription"
    MISSING_CHANNEL_NAME = "Missing channel name"


def capture_exceptions_with_sentry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sentry_client = SentryClient()
        sentry_client.setup()
        response = None
        try:
            response = func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            # Capture the exception in Sentry
            capture_exception(e)
        finally:
            sentry_client.flush()
            return response if response is not None else json.dumps({})

    return wrapper


class BaseError(Exception):
    def __init__(
        self,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error_code: Optional[int] = None,
        error_type: str = ErrorType.INTERNAL
    ):
        self.message = message
        self.data = data
        self.error_code = error_code
        self.error_type = error_type
