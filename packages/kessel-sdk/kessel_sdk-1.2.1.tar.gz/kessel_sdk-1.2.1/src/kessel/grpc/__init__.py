import grpc
import google.auth.transport.grpc
import google.auth.transport.requests

from kessel.auth import GoogleOAuth2ClientCredentials, OAuth2ClientCredentials


def oauth2_call_credentials(credentials: OAuth2ClientCredentials) -> grpc.CallCredentials:
    """
    Create gRPC call credentials from an OAuth2 client.

    Args:
        oauth2_client: An OAuth2ClientCredentials instance.

    Returns:
        grpc.CallCredentials: Call credentials that can be used with gRPC channels.
    """
    auth_plugin = google.auth.transport.grpc.AuthMetadataPlugin(
        credentials=GoogleOAuth2ClientCredentials(credentials),
        request=google.auth.transport.requests.Request(),
    )

    return grpc.metadata_call_credentials(auth_plugin)
