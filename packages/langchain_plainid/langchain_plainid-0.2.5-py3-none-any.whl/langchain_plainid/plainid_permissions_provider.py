import logging
from typing import Any, Dict, List, NamedTuple

from .plainid_client import PlainIDClient
from .plainid_exceptions import PlainIDPermissionsException


class PlainIDEntityAction(NamedTuple):
    """
    Represents an action that can be performed on an entity.

    Attributes:
        name: The entity name
        actions: List of allowed actions for this entity
    """

    name: str
    actions: List[str]


class PlainIDPermissions(NamedTuple):
    """
    NamedTuple representing structured permission data from PlainID.

    Attributes:
        categories: List of category paths user has access to
        entities: List of EntityAction objects representing entity permissions
    """

    categories: List[str] = []
    entities: List[PlainIDEntityAction] = []
    tools: List[str] = []


class PlainIDPermissionsProvider:
    """
    Provides access to user permissions from PlainID.

    This provider calls the get_token endpoint from PlainID client
    to retrieve permissions information.
    """

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        entity_id: str,
        entity_type_id: str,
        plainid_categories_resource_type: str = "categories",
        plainid_entities_resource_type: str = "entities",
        plainid_tools_resource_type: str = "tools_v",
        **kwargs: Any
    ):
        """
        Initialize PlainIDPermissionsProvider with authentication credentials.

        Args:
            base_url (str): Base URL for PlainID service
            client_id (str): Client ID for authentication
            client_secret (str): Client secret for authentication
            entity_id (str): Entity ID for the request
            entity_type_id (str): Entity type ID for the request
            plainid_categories_resource_type (str): Resource type for categories in PlainID
            plainid_entities_resource_type (str): Resource type for entities in PlainID
        """
        self.client = PlainIDClient(base_url, client_id, client_secret, entity_type_id)
        self.kwargs = kwargs
        self.entity_id = entity_id
        self.plainid_categories_resource_type = plainid_categories_resource_type
        self.plainid_entities_resource_type = plainid_entities_resource_type
        self.plainid_tools_resource_type = plainid_tools_resource_type
        try:
            token_data = self.client.get_token(entity_id=self.entity_id, **self.kwargs)
            if token_data is None:
                raise PlainIDPermissionsException(
                    "Failed to retrieve token data from PlainID"
                )

            logging.debug(f"token retrieved: {token_data}")
            permissions = self._extract_permissions(token_data["response"])

            self.permissions = permissions
        except PlainIDPermissionsException as e:
            # Re-raise the exception but bubble it through this component
            raise e
        except Exception as e:
            # Wrap any other exception in our custom exception
            raise PlainIDPermissionsException("Error retrieving permissions", e)

    def get_permissions(self) -> PlainIDPermissions:
        """
        Retrieves permissions information from PlainID's token endpoint.
        Returns:
            PlainIDPermissions: Structured permissions data from PlainID

        Raises:
            PlainIDPermissionsException: If there was an error retrieving or processing permissions
        """
        return self.permissions
    
    def get_allowed_tools(self) -> List[str]:
        """
        Retrieves the list of allowed tools based on the permissions.

        Returns:
            List[str]: List of tool names that the user has access to
        """
        return self.permissions.tools
    def get_allowed_categories(self) -> List[str]:
        """
        Retrieves the list of allowed categories based on the permissions.

        Returns:
            List[str]: List of category paths that the user has access to
        """
        return self.permissions.categories
    
    def get_allowed_entities(self) -> List[PlainIDEntityAction]:
        """
        Retrieves the list of allowed entities based on the permissions.

        Returns:
            List[PlainIDEntityAction]: List of entity actions that the user has access to
        """
        return self.permissions.entities
    
    def _extract_permissions(self, token_data: Dict[str, Any]) -> PlainIDPermissions:
        """
        Extracts and organizes permission data from the PlainID token response.

        Args:
            token_data (Dict[str, Any]): The raw token data from PlainID

        Returns:
            PlainIDPermissions: Structured permissions data
        """
        if not token_data:
            logging.warning("Empty token data received")
            return PlainIDPermissions()

        try:
            # Initialize data structures for permissions
            categories: List[str] = []
            entities: List[PlainIDEntityAction] = []
            tools: List[str] = []

            # Process access permissions from the token response
            if isinstance(token_data, list):
                # Handle the case where token_data is a list (as in the example)
                for item in token_data:
                    self._process_access_permissions_from_item(
                        item, categories, entities, tools
                    )
            elif "access" in token_data:
                # Handle the case where access is directly in token_data
                self._process_access_permissions_from_item(
                    token_data, categories, entities, tools
                )

            return PlainIDPermissions(categories=categories, entities=entities, tools=tools)

        except Exception as e:
            logging.error(f"Error extracting permissions from token data: {str(e)}")
            raise PlainIDPermissionsException(
                "Failed to extract permissions from token data", e
            )

    def _process_access_permissions_from_item(
        self,
        item: Dict[str, Any],
        categories: List[str],
        entities: List[PlainIDEntityAction],
        tools: List[str] = []
    ):
        """
        Process access permissions from a token response item.

        Args:
            item: Dictionary containing access permissions
            categories: List to populate with category paths
            entities: List to populate with entity actions
        """
        if not isinstance(item, dict):
            return

        access_list = item.get("access", [])
        if not isinstance(access_list, list):
            return

        for access_item in access_list:
            path = access_item.get("path")
            resource_type = access_item.get("resourceType")

            if not path or not resource_type:
                continue

            # Handle categories
            if resource_type == self.plainid_categories_resource_type:
                categories.append(path)

            # Handle entities
            elif resource_type == self.plainid_entities_resource_type:
                actions = []
                for action_item in access_item.get("actions", []):
                    action = action_item.get("action")
                    if action:
                        actions.append(action)

                if actions:
                    entities.append(PlainIDEntityAction(name=path, actions=actions))
                    
            elif resource_type == self.plainid_tools_resource_type:
                tools.append(path)

    def get_entities_by_action(
        self, entities: List[PlainIDEntityAction]
    ) -> tuple[List[str], List[str]]:
        """
        Group entities by action type (MASK or ENCRYPT)

        Args:
            entities: List of PlainIDEntityAction objects

        Returns:
            Tuple of (mask_entities, encrypt_entities) as lists of entity names
        """
        mask_entities = []
        encrypt_entities = []

        for entity in entities:
            entity_name = entity.name

            # Check if entity has MASK action
            if "MASK" in entity.actions:
                mask_entities.append(entity_name)

            # Check if entity has ENCRYPT action
            if "ENCRYPT" in entity.actions:
                encrypt_entities.append(entity_name)

        return mask_entities, encrypt_entities
