from math import ceil, floor
from typing import Dict, List, Optional, Tuple

from filum_utils.types.subscription import MetadataGroup, SmartDistributionConfig


class SmartDistributionUtil:
    """Utility class for calculating smart distribution limits based on metadata values."""

    def __init__(
        self,
        smart_config: SmartDistributionConfig,
        total_users_by_metadata_value: Dict[str, int],
        actual_responses_per_metadata: Dict[str, int],
        distribution_limit: Optional[int] = None,
    ):
        """Initialize with smart distribution configuration and user counts.
        
        Args:
            smart_config: Smart distribution configuration
            total_users_by_metadata_value: Dictionary mapping metadata values to user counts
            actual_responses_per_metadata: Dictionary mapping metadata values to actual response counts
            distribution_limit: Optional override for distribution limit
        """
        self._smart_config = smart_config

        # Extract key configuration values
        self._targets = smart_config["targets"]
        self._response_rate = smart_config["response_rate"]
        self._distribution_limit = distribution_limit or 0

        self._default_metadata_groups = self._initialize_default_metadata_groups(
            actual_responses_per_metadata=actual_responses_per_metadata,
            total_users_by_metadata_value=total_users_by_metadata_value
        )

    def calculate_send_limit_per_metadata(self) -> Dict[str, MetadataGroup]:
        """Calculate send limits for each metadata value based on response targets and actual responses.
            
        Returns:
            Dictionary mapping metadata values to MetadataGroup objects with calculated limits
        """
        # Calculate gaps and estimated sends
        metadata_groups, total_estimated_send = self._calculate_gaps_and_estimated_send()
        if total_estimated_send <= 0:
            return self._default_metadata_groups

        # Calculate total sends limit
        total_sends_limit = self._calculate_total_sends_limit(total_estimated_send)

        # Calculate distribution and limits
        metadata_groups = self._calculate_distribution_and_limits(
            metadata_groups, total_estimated_send, total_sends_limit
        )

        # Redistribute any remaining capacity
        return self._redistribute_remaining_capacity(
            metadata_groups, total_sends_limit
        )

    def _initialize_default_metadata_groups(
        self,
        total_users_by_metadata_value: Dict[str, int],
        actual_responses_per_metadata: Dict[str, int],
    ) -> Dict[str, MetadataGroup]:
        """Initialize metadata groups with default values.

        Args:
            total_users_by_metadata_value: Dictionary mapping metadata values to user counts
            actual_responses_per_metadata: Dictionary mapping metadata values to actual response counts

        Returns:
            Dictionary mapping metadata values to MetadataGroup objects
        """
        groups = {}

        for target in self._targets:
            metadata_value = target["metadata_value"]

            actual_responses = actual_responses_per_metadata.get(metadata_value, 0)
            total_users = total_users_by_metadata_value.get(metadata_value, 0)
            groups[metadata_value] = MetadataGroup(
                value=metadata_value,
                target_responses=target["target_responses"],
                actual_responses=actual_responses,
                gap=0,
                estimated_send=0,
                weighted_distribution=0,
                max_send=0,
                send_limit=0,
                remaining_send=0,
                total_users=total_users,
            )

        return groups

    def _calculate_gaps_and_estimated_send(
        self,
    ) -> Tuple[Dict[str, MetadataGroup], int]:
        """Calculate gaps between target and actual responses, and estimated sends needed.

        Returns:
            Tuple containing updated metadata groups and total estimated sends
        """
        total_estimated_send = 0

        formatted_metadata_groups = {}
        for metadata_value, group in self._default_metadata_groups.items():
            # Calculate gap between target and actual responses
            gap = group["target_responses"] - group["actual_responses"]
            # Skip if no gap (target already met)
            if gap <= 0:
                continue

            group["gap"] = gap
            # Calculate estimated sends needed based on response rate
            estimated_send = ceil(gap / self._response_rate)
            group["estimated_send"] = estimated_send
            total_estimated_send += estimated_send
            formatted_metadata_groups[metadata_value] = group

        return formatted_metadata_groups, total_estimated_send

    def _calculate_total_sends_limit(self, total_estimated_send: int) -> int:
        """Calculate the total sends limit based on distribution limit and estimated sends.
        
        Args:
            total_estimated_send: Total estimated sends needed
            
        Returns:
            Total sends limit
        """
        if self._distribution_limit > 0:
            return min(self._distribution_limit, total_estimated_send)

        return total_estimated_send

    def _redistribute_remaining_capacity(
        self,
        metadata_groups: Dict[str, MetadataGroup],
        total_send_limit: int
    ) -> Dict[str, MetadataGroup]:
        """Redistribute remaining capacity across metadata groups.
        
        Args:
            metadata_groups: Mapping of metadata value to its MetadataGroup object
            total_send_limit: Maximum total send limit across all metadata groups
            
        Returns:
            Updated mapping with redistributed send limits
        """
        total_actual_sent = sum(group["send_limit"] for group in metadata_groups.values())

        total_remaining_capacity = total_send_limit - total_actual_sent

        if total_remaining_capacity <= 0:
            return metadata_groups

        extra_send_metadata_groups = self._get_extra_send_metadata_groups(metadata_groups)

        sorted_extra_send_metadata_groups = self._sort_extra_send_metadata_groups(extra_send_metadata_groups)

        # Redistribute capacity among sorted groups
        for metadata_group in sorted_extra_send_metadata_groups:
            metadata_value = metadata_group["value"]
            updated_group, new_remaining_capacity = self._update_metadata_group_send_limit(
                metadata_group, total_remaining_capacity
            )

            metadata_groups[metadata_value] = updated_group

            if new_remaining_capacity == 0:
                break

            total_remaining_capacity = new_remaining_capacity

        return metadata_groups

    @staticmethod
    def _calculate_distribution_and_limits(
        metadata_groups: Dict[str, MetadataGroup],
        total_estimated_send: int,
        total_sends_limit: int
    ) -> Dict[str, MetadataGroup]:
        """Calculate weighted distribution and send limits for each metadata group.

        Args:
            metadata_groups: Dictionary of metadata groups
            total_estimated_send: Total estimated sends needed
            total_sends_limit: Total sends limit

        Returns:
            Updated metadata groups with calculated limits
        """
        formatted_metadata_groups = {}
        for metadata_value, group in metadata_groups.items():
            estimated_send = group["estimated_send"]
            max_send = estimated_send
            if total_estimated_send > 0:
                weighted_distribution = estimated_send / total_estimated_send
                group["weighted_distribution"] = weighted_distribution

                max_send = floor(total_sends_limit * weighted_distribution)

            group["max_send"] = max_send

            send_limit = min(group["total_users"], max_send)
            if not send_limit or send_limit < 0:
                continue

            group["send_limit"] = send_limit
            group["remaining_send"] = send_limit
            formatted_metadata_groups[metadata_value] = group

        return formatted_metadata_groups

    @staticmethod
    def _get_extra_send_metadata_groups(
        metadata_groups: Dict[str, MetadataGroup]
    ) -> List[MetadataGroup]:
        """Get metadata groups that can receive extra capacity.

        Args:
            metadata_groups: Mapping of metadata value to its MetadataGroup object

        Returns:
            List of tuples containing metadata value and group that can receive extra capacity
        """
        extra_send_metadata_groups: List[MetadataGroup] = []

        for metadata_value, group in metadata_groups.items():
            if group["send_limit"] < group["total_users"]:
                extra_send_metadata_groups.append(group)

        return extra_send_metadata_groups

    @staticmethod
    def _sort_extra_send_metadata_groups(
        extra_send_metadata_groups: List[MetadataGroup]
    ) -> List[MetadataGroup]:
        """Sort metadata groups by gap (total_users - send_limit) in descending order.

        Args:
            extra_send_metadata_groups: List of tuples containing metadata value and group

        Returns:
            Sorted list of tuples by gap in descending order
        """
        return sorted(
            extra_send_metadata_groups,
            key=lambda x: x["gap"],
            reverse=True
        )

    @staticmethod
    def _update_metadata_group_send_limit(
        metadata_group: MetadataGroup,
        total_remaining_capacity: int
    ) -> Tuple[MetadataGroup, int]:
        """Update a metadata group's send limit based on remaining capacity.

        Args:
            metadata_group: The MetadataGroup object to update
            total_remaining_capacity: Remaining capacity available for distribution

        Returns:
            Tuple containing updated group and new remaining capacity
        """
        send_limit = metadata_group["send_limit"]
        remaining_capacity = metadata_group["total_users"] - send_limit

        additional_sends = min(total_remaining_capacity, remaining_capacity)

        send_limit += additional_sends
        metadata_group["send_limit"] = send_limit
        metadata_group["remaining_send"] = send_limit

        new_remaining_capacity = total_remaining_capacity - additional_sends

        return metadata_group, new_remaining_capacity
