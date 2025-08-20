"""
Shared HTTP client utilities for registry API calls
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import aiohttp


class HTTPClient:
    """Shared HTTP client with common functionality for registry APIs"""

    _default_timeout: int = 30

    def __init__(self, timeout: Optional[int] = None):
        """Initialize HTTP client with configurable timeout"""
        if timeout is None:
            timeout = getattr(
                self.__class__,
                "_default_timeout",
                int(os.getenv("VERSIONATOR_REQUEST_TIMEOUT", "30")),
            )
        self.timeout = timeout

    async def get_json(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        registry_name: str = "unknown",
        package_name: str = "unknown",
    ) -> Any:
        """
        Make a GET request and return JSON response.

        Args:
            url: The URL to request
            headers: Optional HTTP headers
            registry_name: Name of the registry for error messages
            package_name: Name of the package for error messages

        Returns:
            JSON response as dictionary

        Raises:
            Exception: If request fails or package not found
        """
        if headers is None:
            headers = {"Accept": "application/json"}

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 404:
                    raise Exception(
                        f"Package '{package_name}' not found in {registry_name} registry"
                    )
                elif response.status != 200:
                    text = await response.text()
                    raise Exception(f"{registry_name} API error {response.status}: {text}")

                json_data = await response.json()
                return json_data

    def get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format with Z suffix"""
        return datetime.now(timezone.utc).isoformat() + "Z"
