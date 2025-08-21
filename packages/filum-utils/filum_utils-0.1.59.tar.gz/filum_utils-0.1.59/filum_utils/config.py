import os


class Config:
    APPSTORE_BASE_URL = "https://appstore.filum.asia"
    APPSTORE_USERNAME = "appstore@filum.ai"
    APPSTORE_PASSWORD = ""

    NOTIFICATION_BASE_URL = "https://notification.filum.asia"
    NOTIFICATION_USERNAME = "notification@filum.ai"
    NOTIFICATION_PASSWORD = ""

    SUBSCRIPTION_BASE_URL = "https://subscription.filum.asia"
    SUBSCRIPTION_USERNAME = "subscription@filum"
    SUBSCRIPTION_PASSWORD = ""

    FILUM_BASE_URL = "https://api.filum.asia"
    FILUM_USERNAME = "filum_dev"
    FILUM_PASSWORD = ""

    IAM_BASE_URL = "https://iam.filum.asia"
    IAM_USERNAME = "filum_dev"
    IAM_PASSWORD = ""

    EVENT_API_BASE_URL = "https://event.filum.asia"

    SEGMENT_RECORD_LIMIT = 1000
    FILE_RECORD_LIMIT = 1000

    SURVEY_RESPONSE_LIMIT = 1000
    ENGAGEMENT_MESSAGE_LIMIT = 1000

    GOOGLE_PROJECT_ID = ""
    GOOGLE_PUBSUB_TOPIC_ID = ""
    GOOGLE_PUBSUB_API_ENDPOINT = ""

    GCP_UPLOADS_BUCKET = ""

    SEGMENT_SERVICE_URL = ""
    SEGMENT_SERVICE_USERNAME = ""
    SEGMENT_SERVICE_PASSWORD = ""

    KNOWLEDGE_BASE_SERVICE_URL = ""
    KNOWLEDGE_BASE_SERVICE_USERNAME = ""
    KNOWLEDGE_BASE_SERVICE_PASSWORD = ""

    SENTRY_DSN_URL = ""

    def __init__(self):
        for attr in dir(self):
            if not attr.isupper():
                continue
            default_value = getattr(self, attr)
            value_type = type(default_value)

            value = os.getenv(attr) or default_value

            if value and isinstance(default_value, list) and isinstance(value, str):
                value = value.split(",")
            elif value_type is bool and isinstance(value, str):
                value = value.lower() in ["true", "yes", "t", "i", "1"]
            else:
                value = value_type(value)

            setattr(self, attr, value)


config = Config()
