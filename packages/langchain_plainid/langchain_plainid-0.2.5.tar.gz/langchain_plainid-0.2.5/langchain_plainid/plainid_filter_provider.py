import logging
from typing import (
    Any,
    Dict,
    Optional,
)

from langchain_core.structured_query import (
    Comparator,
    Comparison,
    FilterDirective,
    Operation,
    Operator,
)

from .plainid_client import PlainIDClient
from .plainid_exceptions import PlainIDFilterException

# Configure module logger
logger = logging.getLogger(__name__)


class PlainIDFilterProvider:
    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        entity_id: str,
        entity_type_id: str,
        resource_type: str,
        **kwargs: Any,
    ):
        """
        Initialize PlainIDFilterProvider with authentication credentials.

        Args:
                base_url (str): Base URL for PlainID service
                client_id (str): Client ID for authentication
                client_secret (str): Client secret for authentication
                entity_id (str): Entity ID for the request
                entity_type_id (str): Entity type ID for the request
                resource_type (str): Resource type for the request
        """
        self.entity_id = entity_id
        self.kwargs = kwargs
        self.client = PlainIDClient(base_url, client_id, client_secret, entity_type_id)
        self.resource_type = resource_type

    def get_filter(self) -> Optional[FilterDirective]:
        """
        Returns a filter that can be used to filter documents in the vector store.
        Uses FilterDirective from langchain_core.structured_query.

        Returns:
                Optional[FilterDirective]: Filter directive from PlainID

        Raises:
                PlainIDFilterException: If there was an error processing the filter
        """
        try:
            resolution = self.client.get_resolution(
                self.entity_id, [self.resource_type],**self.kwargs
            )

            if not resolution:
                return None

            structured_filter = self._map_plainid_resoulution_to_filter(resolution)
            logger.debug("filter: %s", structured_filter)

            return structured_filter
        except PlainIDFilterException as e:
            # Re-raise the exception but mark that it bubbled through this component
            raise e.bubble_through("PlainIDFilterProvider")
        except Exception as e:
            # Wrap any other exception in our custom exception
            raise PlainIDFilterException("Error retrieving filter", e)

    def _map_plainid_resoulution_to_filter(
        self, resolution: Dict[str, Any]
    ) -> Optional[FilterDirective]:
        if not resolution or "response" not in resolution:
            logger.warning("Invalid resolution format - missing 'response' field")
            return None

        try:
            # Navigate to the asset-attributes-filter section
            responses = resolution.get("response", [])
            if not responses:
                return None

            all_filters = []

            # Iterate through all responses
            for response in responses:
                privileges = response.get("privileges", {})
                allowed = privileges.get("allowed", [])

                # Iterate through all allowed rules
                for allowed_rule in allowed:
                    if allowed_rule.get("resourceType") != self.resource_type:
                        continue

                    actions = allowed_rule.get("actions", [])

                    # Iterate through all actions
                    for action in actions:
                        asset_attributes_filter = action.get(
                            "asset-attributes-filter", {}
                        )
                        if asset_attributes_filter:
                            # Convert the filter structure
                            converted_filter = self._convert_plainid_filter(
                                asset_attributes_filter
                            )
                            if converted_filter:
                                all_filters.append(converted_filter)

            # If we have no filters, return None
            if not all_filters:
                return None

            # If we have only one filter, return it directly
            if len(all_filters) == 1:
                return all_filters[0]

            # If we have multiple filters, join them with OR operator
            return Operation(operator=Operator.OR, arguments=all_filters)

        except Exception as e:
            logger.error(f"Error mapping PlainID filter: {str(e)}")
            raise PlainIDFilterException(
                "Failed to map PlainID resolution to filter", e
            )

    def _convert_plainid_filter(
        self, filter_part: Dict[str, Any]
    ) -> Optional[FilterDirective]:
        """
        Recursively converts a part of the PlainID filter structure to a FilterDirective.

        Args:
                filter_part (Dict[str, Any]): A part of the PlainID filter structure

        Returns:
                Optional[FilterDirective]: The corresponding structured filter part
        """
        # Handle AND conditions
        if "AND" in filter_part:
            and_conditions = filter_part["AND"]
            converted_conditions = []
            for condition in and_conditions:
                converted = self._convert_condition(condition)
                if converted:  # Only add non-empty conditions
                    converted_conditions.append(converted)

            if converted_conditions:
                return Operation(operator=Operator.AND, arguments=converted_conditions)
            return None

        # Handle OR conditions
        elif "OR" in filter_part:
            or_conditions = filter_part["OR"]
            converted_conditions = []
            for condition in or_conditions:
                # Check if this is a nested operation (AND/OR) or a simple condition
                if "AND" in condition or "OR" in condition:
                    # This is a nested operation, convert recursively
                    converted = self._convert_plainid_filter(condition)
                else:
                    # This is a simple condition
                    converted = self._convert_condition(condition)
                if converted:  # Only add non-empty conditions
                    converted_conditions.append(converted)

            if converted_conditions:
                return Operation(operator=Operator.OR, arguments=converted_conditions)
            return None

        return None

    def _convert_condition(
        self, condition: Dict[str, Any]
    ) -> Optional[FilterDirective]:
        """
        Converts a PlainID condition to a FilterDirective.

        Args:
                condition (Dict[str, Any]): A PlainID condition

        Returns:
                Optional[FilterDirective]: The corresponding Comparison object

        Raises:
                ValueError: When an unsupported operator is encountered
        """
        attribute = condition.get("attribute")
        operator = condition.get("operator")
        values = condition.get("values", [])

        if not attribute or not operator:
            return None

        # Map PlainID operators to langchain_core.structured_query comparators
        operator_mapping = {
            "IN": Comparator.IN,
            "NOT_IN": Comparator.NIN,
            "EQUALS": Comparator.EQ,
            "LESS": Comparator.LT,
            "GREATE": Comparator.GT,
            "GREAT_EQUALS": Comparator.GTE,
            "LESS_EQUALS": Comparator.LTE,
            "CONTAINS": Comparator.CONTAIN,
            "STARTWITH": Comparator.LIKE,
            "ENDWITH": Comparator.LIKE,
            "NOTEQUALS": Comparator.NE,
        }

        if operator in operator_mapping:
            if (
                operator_mapping[operator]
                in [
                    Comparator.EQ,
                    Comparator.NE,
                    Comparator.GT,
                    Comparator.LT,
                    Comparator.GTE,
                    Comparator.LTE,
                ]
                and values
            ):
                # Handle type conversion for numeric values
                value = values[0]
                if condition.get("type") == "INTEGER":
                    if value.replace(".", "", 1).isdigit():
                        value = float(value)

                return Comparison(
                    comparator=operator_mapping[operator],
                    attribute=attribute,
                    value=value,
                )

            # For multi-value operators
            if operator_mapping[operator] in [Comparator.IN, Comparator.NIN]:
                # Handle type conversion for numeric values in lists
                if condition.get("type") == "INTEGER":
                    converted_values = [
                        float(val) if val.replace(".", "", 1).isdigit() else val
                        for val in values
                    ]
                    return Comparison(
                        comparator=operator_mapping[operator],
                        attribute=attribute,
                        value=converted_values,
                    )
                return Comparison(
                    comparator=operator_mapping[operator],
                    attribute=attribute,
                    value=values,
                )

            # For pattern matching operators (CONTAINS)
            if operator_mapping[operator] == Comparator.CONTAIN and values:
                value = values[0]
                return Comparison(
                    comparator=Comparator.CONTAIN,
                    attribute=attribute,
                    value=value,
                )

            # For LIKE operators (STARTWITH, ENDWITH)
            if operator_mapping[operator] == Comparator.LIKE and values:
                value = values[0]
                # Adjust the pattern based on operator
                if operator == "STARTWITH":
                    value = f"{value}%"  # Add wildcard at the end
                elif operator == "ENDWITH":
                    value = f"%{value}"  # Add wildcard at the beginning

                return Comparison(
                    comparator=Comparator.LIKE,
                    attribute=attribute,
                    value=value,
                )
        else:
            error_msg = f"Unknown operator: {operator}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        return None
