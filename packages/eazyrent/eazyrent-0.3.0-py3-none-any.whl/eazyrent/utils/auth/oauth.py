import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List
from urllib.parse import urlencode

import jwt
import urllib3
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError

from .schemas import ClientCredentials, JsonKey

http = urllib3.PoolManager()

logger = logging.getLogger(__name__)


class OAuth:

    auth_server: str = os.environ.get("EAZ_AUTH_SERVER", "https://auth.eazyrent.fr")
    token_endpoint: str = "/oauth/v2/token"
    eazyrent_project: str = os.environ.get("EAZ_PROJECT_ID", "310976816384838665")

    @classmethod
    def get_scopes(cls, additional_scopes: List[str] = []) -> str:
        scopes = [
            "urn:zitadel:iam:org:projects:roles",
            "urn:zitadel:iam:user:resourceowner",
            f"urn:zitadel:iam:org:project:id:{cls.eazyrent_project}:aud",
        ] + additional_scopes
        return " ".join(scopes)

    @classmethod
    def generate_jwt_bearer(cls, key: JsonKey) -> str:
        """
        Generate a signed JWT (JSON Web Token) to be used as an assertion in the
        OAuth 2.0 JWT Bearer Token flow (RFC 7523).

        This JWT includes standard claims such as:
            - `iss` (issuer): the service account's user ID.
            - `sub` (subject): the same as the issuer in this context.
            - `aud` (audience): the token endpoint of the authorization server.
            - `iat` (issued at): the current UTC timestamp.
            - `exp` (expiration): 5 minutes after the issued time.

        The JWT is signed using the RS256 algorithm and includes the `kid` (key ID)
        in the header to help the authorization server locate the correct public key.

        Args:
            key (JsonKey): The service account credentials used to build and sign
            the JWT, including the private key and metadata.

        Returns:
            str: A signed JWT string to be used as an OAuth 2.0 assertion.

        Reference:
            https://datatracker.ietf.org/doc/html/rfc7523#section-2.2
        """
        payload = {
            "iss": key.user_id,
            "sub": key.user_id,
            "aud": cls.auth_server,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=300),
            "iat": datetime.now(timezone.utc),
        }
        headers = {"alg": "RS256", "kid": key.key_id}
        return jwt.encode(
            payload, key.key.get_secret_value(), algorithm="RS256", headers=headers
        )

    @classmethod
    def client_credentials_flow(cls, credentials: ClientCredentials) -> str:
        """
        Perform the OAuth 2.0 Client Credentials flow to obtain an access token.

        This method implements the "Client Credentials Grant" as defined in
        RFC 6749, Section 4.4. It is typically used for machine-to-machine
        authentication where a client (e.g., backend service) authenticates
        itself using a client ID and secret, without user involvement.

        Args:
            credentials (ClientCredentials): An object containing the access key
            ID (as `key`) and the client secret (as `secret`).

        Returns:
            str: The OAuth 2.0 access token issued by the authorization server.

        Raises:
            AuthenticationError: If the token request fails due to invalid credentials
            or server-side issues.

        Reference:
            https://datatracker.ietf.org/doc/html/rfc6749#section-4.4
        """

        data = urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": credentials.key,
                "client_secret": credentials.secret.get_secret_value(),
                "scope": cls.get_scopes(),
            }
        )

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = http.request(
            "POST",
            cls.auth_server + cls.token_endpoint,
            body=data,
            headers=headers,
        )

        if response.status != 200:
            err = f"{response.status} - {response.data.decode()}"
            raise RuntimeError(f"Client credentials auth failed: {err}")

        return json.loads(response.data.decode("utf-8"))["access_token"]

    def validate_jwt_access_key(cls, access_token: str) -> None:
        """
        Validate a JWT access token by checking its expiration (`exp`) claim.

        This method decodes the JWT without verifying the signature and checks
        whether the token has expired based on the current UTC time. If the token
        is expired or malformed, an appropriate exception is raised.

        Args:
            access_token (str): The JWT access token to validate.

        Raises:
            jwt.ExpiredSignatureError: If the token has expired.
            jwt.DecodeError: If the token cannot be decoded.
            jwt.InvalidTokenError: For other issues related
                to token structure or content.

        Note:
            This function assumes the token is a valid JWT and uses `jwt.decode`
            with `options={"verify_signature": False}`. It should not be used
            for authorization decisions, only for expiration checks.

        Reference:
            https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.4
        """
        try:
            jwt.decode(
                access_token,
                options={"verify_signature": False, "verify_exp": True},
                algorithms=["RS256"],
            )
        except ExpiredSignatureError:
            logger.error("Access token has expired.")
            raise
        except DecodeError:
            logger.error("Access token could not be decoded.")
            raise
        except InvalidTokenError:
            logger.error("Invalid access token.")
            raise

    @classmethod
    def jwt_bearer_client_credentials(cls, credentials: JsonKey) -> str:
        """
        Perform the OAuth 2.0 JWT Bearer Token flow to obtain an access token.

        This method implements the "JSON Web Token (JWT) Bearer Token Flow"
        as defined in RFC 7523, Section 2. It is typically used by service
        accounts or applications that authenticate with an authorization server
        by presenting a signed JWT assertion instead of traditional client credentials.

        The JWT is signed using a private key associated with the service account
        and includes claims such as the issuer, subject, audience, and expiration.

        Args:
            credentials (JsonKey): An object containing the service account's JWT
            key and associated metadata (e.g., key ID, user ID, expiration date).

        Returns:
            str: The OAuth 2.0 access token issued by the authorization server.

        Raises:
            RuntimeError: If the token request fails or the authorization server
            responds with an error.

        Reference:
            https://datatracker.ietf.org/doc/html/rfc7523#section-2
        """
        data = urlencode(
            {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "scope": cls.get_scopes(),
                "assertion": cls.generate_jwt_bearer(credentials),
            }
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = http.request(
            "POST",
            cls.auth_server + cls.token_endpoint,
            body=data,
            headers=headers,
        )
        if response.status != 200:
            err = f"{response.status} - {response.data.decode()}"
            raise RuntimeError(f"Client credentials auth failed: {err}")

        return json.loads(response.data.decode("utf-8"))["access_token"]
