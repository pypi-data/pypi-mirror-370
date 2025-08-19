PROPERTY_PLACEHOLDER_REGEX = r'\{{[^{}]*\}}'
TRANSLATION_FORMAT_REGEX = r'question.[\d].option.[\d]'


class BaseEnum:
    @classmethod
    def get_list(cls):
        return [getattr(cls, attr) for attr in dir(cls) if attr.isupper()]


class ObjectName(BaseEnum):
    SEGMENT = "Segment"
    EVENT = "Event"
    CAMPAIGN = "Campaign"
    USER = "User"
    SURVEY_RESPONSE = "Response"
    CONVERSATION = "Conversation"


class VariableProperty:
    ID = "ID"
    LINK = "Link"
    USER_PHONE = "Phone"
    USER_EMAIL = "Email"
    RATING = "Rating"
    TEXT = "Text"
    USER = "User"
    NAME = "Name"
    SIZE = "Size"
    METRIC_TYPE = "Metric_Type"


class UserProperty:
    ID = "User ID"
    NAME = "Name"
    EMAIL = "Email"
    PHONE = "Phone"


class SurveyAnsweredEventProperty:
    USER_EMAIL = "User Email"
    USER_PHONE = "User Phone"
    SURVEY_RESPONSE_ID = "Survey Response ID"
    RATING = "Rating"
    METRIC_TYPE = "Metric Type"
    TEXT = "Follow Up Text"
    SURVEY_ID = "Survey ID"
    EVENT_NAME = "Event Name"
    REVIEW_KEY = "_keys"
    LOCATION_ID = "Location ID"


class ConversationProperty:
    ID = "ID"


class SurveyResponseProperty:
    ID = "ID"


class CampaignProperty:
    ID = "ID"
    NAME = "Name"


class SegmentProperty:
    ID = "id"
    NAME = "name"
    TOTAL_USERS = "total_users"
