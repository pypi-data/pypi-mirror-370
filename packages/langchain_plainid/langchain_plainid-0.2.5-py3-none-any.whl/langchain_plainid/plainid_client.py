import json
import logging
from typing import Any, Dict

import requests

from .plainid_exceptions import PlainIDClientException

# Configure module logger
logger = logging.getLogger(__name__)


class PlainIDClient:
    def __init__(
        self, base_url: str, client_id: str, client_secret: str, entity_type_id: str
    ):
        """
        Initialize PlainIDClient with authentication credentials.

        Args:
            base_url (str): Base URL for PlainID service
            client_id (str): Client ID for authentication
            client_secret (str): Client secret for authentication
            entity_type_id (str): Entity type ID for the request
        """
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.entity_type_id = entity_type_id

    def get_resolution(
        self,
        entity_id: str,
        resouce_full_paths: list[str] = [],
        include_attributes: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Gets resolution data from PlainID API.

        Args:
            entity_id (str): The entity ID to get resolution for
            include_attributes (bool): Whether to include attributes in the response
            **kwargs: Additional fields to include in the request payload

        Returns:
            Dict[str, Any]: Resolution data from PlainID

        Raises:
            PlainIDClientException: If there was an error fetching the resolution
        """
        try:
            logger.debug("getting resolution... %s", entity_id)
            headers = {
                "Content-Type": "application/json",
            }

            payload = {
                "clientId": self.client_id,
                "clientSecret": self.client_secret,
                "entityId": entity_id,
                "entityTypeId": self.entity_type_id,
                "includeAttributes": include_attributes,
            }

            if resouce_full_paths:
                payload["environment"] = {"resourceFullPath": resouce_full_paths}

            # Add any additional kwargs to the payload
            payload.update(kwargs)

            logger.debug("payload: %s", payload)
            response = requests.post(
                f"{self.base_url}/runtime/resolution/v3",
                headers=headers,
                data=json.dumps(payload),
            )

            response.raise_for_status()
            resolution = response.json()
            logger.debug("resolution: %s", resolution)
            return resolution

        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error response: %s", response.text)
            raise PlainIDClientException(
                f"Failed to fetch resolution for entity {entity_id}, status code: {response.status_code}, response: {response.text}",
                e,
            )
        except (json.JSONDecodeError, requests.exceptions.RequestException) as e:
            error_msg = getattr(response, "text", str(e))
            logger.error("Error with PlainID resolution request: %s", error_msg)
            raise PlainIDClientException(
                f"Failed to process resolution request for entity {entity_id}: {error_msg}",
                e,
            )
        except Exception as e:
            logger.error("Unexpected error in get_resolution: %s", str(e))
            raise PlainIDClientException(
                f"Unexpected error when fetching resolution for entity {entity_id}", e
            )

    def get_token(
        self, entity_id: str = "user", include_attributes: bool = True, **kwargs
    ) -> Dict[str, Any]:
        """
        Gets token data from PlainID API.

        Args:
            entity_id (str): The entity ID to get resolution for
            include_attributes (bool): Whether to include attributes in the response
            **kwargs: Additional fields to include in the request payload

        Returns:
            Dict[str, Any]: Topic data from PlainID

        Raises:
            PlainIDClientException: If there was an error fetching the token
        """
        try:
            headers = {
                "Content-Type": "application/json",
            }
            payload = {
                "clientId": self.client_id,
                "clientSecret": self.client_secret,
                "entityId": entity_id,
                "entityTypeId": self.entity_type_id,
                "includeAttributes": include_attributes,
            }

            # Add any additional kwargs to the payload
            payload.update(kwargs)

            logger.debug("payload: %s", payload)

            response = requests.post(
                f"{self.base_url}/runtime/token/v3",
                headers=headers,
                data=json.dumps(payload),
            )

            response.raise_for_status()
            resolution = response.json()
            logger.debug("plaind id client response : %s", resolution)
            logger.debug("token: %s", resolution)
            return resolution

        except requests.exceptions.HTTPError as e:
            logger.error("HTTP error response: %s", response.text)
            raise PlainIDClientException(
                f"Failed to fetch token for entity {entity_id}, status code: {response.status_code}, response: {response.text}",
                e,
            )
        except (json.JSONDecodeError, requests.exceptions.RequestException) as e:
            error_msg = getattr(response, "text", str(e))
            logger.error("Error with PlainID token request: %s", error_msg)
            raise PlainIDClientException(
                f"Failed to process token request for entity {entity_id}: {error_msg}",
                e,
            )
        except Exception as e:
            logger.error("Unexpected error in get_token: %s", str(e))
            raise PlainIDClientException(
                f"Unexpected error when fetching token for entity {entity_id}", e
            )
