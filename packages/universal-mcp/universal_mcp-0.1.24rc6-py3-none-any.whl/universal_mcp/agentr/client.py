import os

import httpx
from loguru import logger

from universal_mcp.config import AppConfig
from universal_mcp.exceptions import NotAuthorizedError


class AgentrClient:
    """Helper class for AgentR API operations.

    This class provides utility methods for interacting with the AgentR API,
    including authentication, authorization, and credential management.

    Args:
        api_key (str, optional): AgentR API key. If not provided, will look for AGENTR_API_KEY env var
        base_url (str, optional): Base URL for AgentR API. Defaults to https://api.agentr.dev
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        base_url = base_url or os.getenv("AGENTR_BASE_URL", "https://api.agentr.dev")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("AGENTR_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided and AGENTR_API_KEY not found in environment variables")
        self.client = httpx.Client(
            base_url=self.base_url, headers={"X-API-KEY": self.api_key}, timeout=30, follow_redirects=True
        )

    def get_credentials(self, integration_name: str) -> dict:
        """Get credentials for an integration from the AgentR API.

        Args:
            integration_name (str): Name of the integration to get credentials for

        Returns:
            dict: Credentials data from API response

        Raises:
            NotAuthorizedError: If credentials are not found (404 response)
            HTTPError: For other API errors
        """
        response = self.client.get(
            f"/api/{integration_name}/credentials/",
        )
        if response.status_code == 404:
            logger.warning(f"No credentials found for {integration_name}. Requesting authorization...")
            action = self.get_authorization_url(integration_name)
            raise NotAuthorizedError(action)
        response.raise_for_status()
        return response.json()

    def get_authorization_url(self, integration_name: str) -> str:
        """Get authorization URL for an integration.

        Args:
            integration_name (str): Name of the integration to get authorization URL for

        Returns:
            str: Message containing authorization URL

        Raises:
            HTTPError: If API request fails
        """
        response = self.client.get(f"/api/{integration_name}/authorize/")
        response.raise_for_status()
        url = response.json()
        return f"Please ask the user to visit the following url to authorize the application: {url}. Render the url in proper markdown format with a clickable link."

    def fetch_apps(self) -> list[AppConfig]:
        """Fetch available apps from AgentR API.

        Returns:
            List of application configurations

        Raises:
            httpx.HTTPError: If API request fails
        """
        response = self.client.get("/api/apps/")
        response.raise_for_status()
        data = response.json()
        return [AppConfig.model_validate(app) for app in data]

    def fetch_app(self, app_id: str) -> dict:
        """Fetch a specific app from AgentR API.

        Args:
            app_id (str): ID of the app to fetch

        Returns:
            dict: App configuration data

        Raises:
            httpx.HTTPError: If API request fails
        """
        response = self.client.get(f"/apps/{app_id}/")
        response.raise_for_status()
        return response.json()

    def list_all_apps(self) -> list:
        """List all apps from AgentR API.

        Returns:
            List of app names
        """
        response = self.client.get("/apps/")
        response.raise_for_status()
        return response.json()

    def list_actions(self, app_id: str):
        """List actions for an app.

        Args:
            app_id (str): ID of the app to list actions for

        Returns:
            List of action configurations
        """

        response = self.client.get(f"/apps/{app_id}/actions/")
        response.raise_for_status()
        return response.json()
