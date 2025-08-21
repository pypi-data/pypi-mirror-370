import datetime
from typing import Tuple

import google.auth.credentials
import google.auth.transport.requests
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


class OIDCDiscoveryMetadata:
    """
    Represents OIDC discovery metadata.
    """

    def __init__(self, discovery_document: dict):
        self._document = discovery_document

    @property
    def token_endpoint(self) -> str:
        return self._document["token_endpoint"]


def fetch_oidc_discovery(issuer_url: str) -> OIDCDiscoveryMetadata:
    """
    Fetches OIDC discovery metadata from the provider.

    This function makes a network request to the OIDC provider's discovery endpoint
    to retrieve the provider's metadata including the token endpoint.

    Args:
        issuer_url: The base URL of the OIDC provider.

    Returns:
        OIDCDiscoveryMetadata containing the discovered endpoints.

    Raises:
        requests.exceptions.RequestException: If the discovery document cannot be retrieved.
        ValueError: If the response is not valid JSON.
    """
    discovery_url = f"{issuer_url.rstrip('/')}/.well-known/openid-configuration"
    response = requests.get(discovery_url, timeout=10)
    response.raise_for_status()
    config = response.json()

    return OIDCDiscoveryMetadata(config)


class OAuth2ClientCredentials:
    """
    OAuth2ClientCredentials class for handling the OAuth 2.0 Client Credentials flow.

    Integrates with the google-auth and requests-oauthlib library to fetch an access token
    from a specified token endpoint with automatic refreshing.

    This class only accepts a direct token URL. For OIDC discovery, use the
    fetch_oidc_discovery function to obtain the token endpoint first.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_endpoint: str,
    ):
        """
        Initializes the OAuth2ClientCredentials.

        Args:
            client_id: The client ID for the application.
            client_secret: The client secret for the application.
            token_endpoint: The direct token endpoint URL.
        """
        self._token_endpoint = token_endpoint
        self._client_id = client_id
        self._client_secret = client_secret

        client = BackendApplicationClient(client_id=self._client_id)
        self._session = OAuth2Session(client=client)

        self._token = None
        self._expiry = None

    def get_token(self, force_refresh: bool = False) -> Tuple[str, datetime.datetime]:
        """
        Get a valid access token, refreshing if necessary or forced.

        Args:
            force_refresh: If True, forces token refresh regardless of expiry.

        Returns:
            Tuple containing (access_token, expires_at).
        """
        current_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

        if (
            force_refresh
            or self._token is None
            or self._expiry is None
            or self._expiry <= current_time + datetime.timedelta(seconds=300)
        ):
            # Refresh the token
            token_data = self._session.fetch_token(
                token_url=self._token_endpoint,
                client_id=self._client_id,
                client_secret=self._client_secret,
            )

            self._token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 0)
            self._expiry = current_time + datetime.timedelta(seconds=expires_in)

        return (self._token, self._expiry)


class GoogleOAuth2ClientCredentials(google.auth.credentials.Credentials):
    """
    Adapter class that implements google.auth.credentials.Credentials interface
    for OAuth2ClientCredentials.
    """

    def __init__(self, credentials: OAuth2ClientCredentials):
        """
        Initialize the credentials adapter.

        Args:
            credentials: The OAuth2ClientCredentials instance to adapt.
        """
        self._credentials = credentials
        super().__init__()

    @property
    def token(self) -> str:
        return self._credentials._token

    @token.setter
    def token(self, value: str) -> None:
        self._credentials._token = value

    @property
    def expiry(self) -> datetime.datetime:
        return self._credentials._expiry

    @expiry.setter
    def expiry(self, value: datetime.datetime) -> None:
        self._credentials._expiry = value

    def refresh(self, request: google.auth.transport.requests.Request) -> None:
        self._credentials.get_token(force_refresh=True)
