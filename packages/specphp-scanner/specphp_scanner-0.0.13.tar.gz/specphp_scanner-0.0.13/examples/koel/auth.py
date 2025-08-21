"""Example Koel authentication implementation."""
from __future__ import annotations

import requests

from specphp_scanner.auth.base import BaseAuth


class KoelAuth(BaseAuth):
    """Koel authentication implementation.

    This is an example implementation showing how to create a custom
    authentication class for the Koel music streaming application.
    """

    def __init__(self, email: str, password: str):
        """Initialize Koel authentication.

        Args:
            email: Koel user email
            password: Koel user password
        """
        self.email = email
        self.password = password
        self._token: str | None = None

    def authenticate(self, base_url: str) -> None:
        """Authenticate with Koel API.

        Args:
            base_url: The base URL of the Koel API
        """
        url = f"{base_url}/api/me"
        response = requests.post(
            url, json={
                'email': self.email,
                'password': self.password,
            },
        )

        if response.status_code != 200:
            raise Exception(f"Authentication failed: {response.text}")

        self._token = response.json()['token']

    def get_headers(self, base_url: str) -> dict[str, str]:
        """Get authentication headers.

        Args:
            base_url: The base URL of the API

        Returns:
            Dict containing authentication headers
        """
        if not self._token:
            self.authenticate(base_url)

        return {
            'Authorization': f"Bearer {self._token}",
        }

    def get_cookies(self, base_url: str) -> dict[str, str]:
        """Get authentication cookies.

        Args:
            base_url: The base URL of the API

        Returns:
            Empty dict as Koel uses token-based auth
        """
        return {}
