import sentry_sdk
from sentry_sdk.integrations.gcp import GcpIntegration

from filum_utils.config import config


class SentryHintKey:
    LOG_RECORD = "log_record"
    EXC_INFO = "exc_info"


class SentryClient:
    @classmethod
    def setup(cls):
        sentry_sdk.init(
            dsn=config.SENTRY_DSN_URL,
            integrations=[GcpIntegration()],
            traces_sample_rate=0,
            before_send=cls.before_send,
        )

    @staticmethod
    def before_send(event, hint):
        if SentryHintKey.LOG_RECORD in hint:
            return None

        return event

    @classmethod
    def flush(cls):
        sentry_sdk.flush()
