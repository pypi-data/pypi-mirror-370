from datetime import date
from typing import Dict, List, Optional

from tenacity import retry, stop_after_attempt, wait_fixed

from filum_utils.clients.common import BaseClient
from filum_utils.config import config
from filum_utils.enums import Organization
from filum_utils.types.engagement_message import CreateEngagementMessage
from filum_utils.types.survey_response import CreateSurveyResponse
from filum_utils.utils.datetime_formatter import DateTimeFormatter

_RETRY_PARAMS = {
    "wait": wait_fixed(10),
    "stop": stop_after_attempt(3),
}


class FilumClient(BaseClient):
    def __init__(self):
        super().__init__(
            base_url=config.FILUM_BASE_URL,
            username=config.FILUM_USERNAME,
            password=config.FILUM_PASSWORD,
        )

    def get_automated_action(self, automated_action_id: int):
        return self._request(
            method="GET", endpoint=f"/internal/automated-actions/{automated_action_id}"
        )

    def get_campaign(self, campaign_id: str):
        return self._request(
            method="GET", endpoint=f"/internal/survey-campaigns/{campaign_id}"
        )

    def get_segment(self, segment_id: str, organization: Organization):
        return self._request(
            method="GET",
            endpoint=f"/internal/segments/{segment_id}",
            params={
                "organization_id": organization["id"],
                "organization_slug": organization["slug"],
            },
        )

    def update_campaign_subscription_status(
        self, campaign_id: str, subscription_id: str, updated_status: str
    ):
        return self._request(
            method="PUT",
            endpoint=f"/internal/survey-campaigns/{campaign_id}/subscription-webhooks",
            data={"subscription_id": subscription_id, "status": updated_status},
        )

    def update_engagement_campaign_subscription_status(
        self,
        organization_id: str,
        campaign_id: str,
        distribution_id: str,
        updated_status: str,
    ):
        return self._request(
            method="PUT",
            endpoint=f"/internal/engagement-campaigns/{campaign_id}/distributions/{distribution_id}/status",
            params={"organization_id": organization_id},
            data={"status": updated_status},
        )

    def get_user_csv_reader(
        self,
        custom_properties: List[str],
        segment_id: str,
        organization: Organization,
        limit: int = config.SEGMENT_RECORD_LIMIT,
        offset: int = 0,
        user_properties: Optional[List[str]] = None,
    ):
        return self._request(
            method="POST",
            endpoint="/internal/users/export",
            data={
                "organization_id": organization["id"],
                "organization_slug": organization["slug"],
                "segment_id": segment_id,
                "custom_properties": custom_properties,
                "user_properties": user_properties,
                "offset": offset,
                "limit": limit,
            },
            timeout=300,
        )

    def get_uploaded_file(self, file_name):
        return self._request(
            method="POST",
            endpoint="/internal/download-file",
            data={
                "file_name": file_name,
            },
        )

    @retry(**_RETRY_PARAMS)
    def create_survey_responses(
        self, campaign_id: str, responses: List[CreateSurveyResponse]
    ):
        return self._request(
            method="POST",
            endpoint=f"/internal/survey-campaigns/{campaign_id}/survey-responses/batch",
            data=responses,
        )

    @retry(**_RETRY_PARAMS)
    def create_engagement_messages(
        self,
        organization_id: str,
        campaign_id: str,
        messages: List[CreateEngagementMessage],
    ):
        return self._request(
            method="POST",
            endpoint=f"/internal/engagement-campaigns/{campaign_id}/messages/batch",
            params={"organization_id": organization_id},
            data=messages,
        )

    @retry(**_RETRY_PARAMS)
    def get_sent_engagement_message_count(
        self, organization_id: str, campaign_id: str, day: date
    ):
        return self._request(
            method="GET",
            endpoint=f"/internal/engagement-campaigns/{campaign_id}/sent-message-count",
            params={
                "organization_id": organization_id,
                "day": day.isoformat(),
            },
        )

    @retry(**_RETRY_PARAMS)
    def get_this_month_answered_response_counts_by_metadata(
        self, organization_id: str, campaign_id: str, metadata_id: str, source: str
    ) -> Dict[str, int]:
        """Retrieve total survey responses for each metadata value for current month.

        Args:
            organization_id (str): ID of the organization
            campaign_id (str): ID of the campaign
            metadata_id (str): Metadata ID
            source (str)

        Returns:
            Dict[str, int]: Mapping from metadata value to survey response count
        """
        # Get the first date of the current month as start_date
        current_datetime = DateTimeFormatter.get_current_datetime()
        start_date = current_datetime.replace(day=1).date()
        # Get the current date as end_date
        end_date = current_datetime.date()

        return self._request(
            method="GET",
            endpoint=f"/internal/survey-campaigns/{campaign_id}/answered-response-counts",
            params={
                "organization_id": organization_id,
                "metadata_id": metadata_id,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "source": source,
            },
        )
