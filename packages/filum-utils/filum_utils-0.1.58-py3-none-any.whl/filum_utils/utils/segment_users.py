from typing import Any, Dict, List


class SegmentUserUtil:
    """Utility class for working with segment users data."""

    @classmethod
    def count_grouped_users_by_metadata_value(
        cls,
        users: List[Dict[str, Any]],
        property_name: str
    ) -> Dict[str, int]:
        """Count users grouped by a specific property value.
        
        Args:
            users: List of user dictionaries
            property_name: Key to group users by
            
        Returns:
            Dictionary mapping metadata values to user counts
        """
        total_users_by_metadata_value = {}
        for user in users:
            value = user.get(property_name, "")
            if not value:
                continue

            value = str(value)
            current_total_user = total_users_by_metadata_value.get(value, 0)
            total_users_by_metadata_value[value] = current_total_user + 1

        return total_users_by_metadata_value
