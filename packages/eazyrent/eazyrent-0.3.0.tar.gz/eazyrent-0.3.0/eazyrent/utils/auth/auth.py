import json
import logging
import os
from configparser import ConfigParser
from pathlib import Path
from typing import Literal, Tuple

from pydantic import SecretStr

from .oauth import OAuth
from .schemas import ApiKey, ClientCredentials, JsonKey

logger = logging.getLogger(__name__)


CREDENTIALS_TYPES = [
    {"type": "API_KEY", "keys": ["EAZ_API_KEY"]},
    {"type": "JSON", "keys": ["EAZ_JSON_KEY"]},
    {
        "type": "CLIENT_CREDENTIALS",
        "keys": ["EAZ_ACCESS_KEY_ID", "EAZ_SECRET_ACCESS_KEY"],
    },
]


class Auth:
    @staticmethod
    def get_credentials_from_environment():
        """Get credentials from environment variables (with EAZ_ prefix)."""
        for credentials_type in CREDENTIALS_TYPES:
            if all([os.environ.get(key) for key in credentials_type["keys"]]):
                try:
                    if credentials_type["type"] == "API_KEY":
                        return ApiKey(token=SecretStr(os.environ["EAZ_API_KEY"]))

                    elif credentials_type["type"] == "CLIENT_CREDENTIALS":
                        return ClientCredentials(
                            key=os.environ["EAZ_ACCESS_KEY_ID"],
                            secret=SecretStr(os.environ["EAZ_SECRET_ACCESS_KEY"]),
                        )

                    elif credentials_type["type"] == "JSON":
                        json_raw = os.environ["EAZ_JSON_KEY"]
                        try:
                            json_path = Path(json_raw).expanduser()
                            if json_path.exists():
                                with open(json_path) as f:
                                    data = json.load(f)
                        except Exception:
                            data = json.loads(json_raw)
                        return JsonKey(**data)

                except Exception as e:
                    logger.error(f"Invalid credentials from environment: {e}")
        return None

    @staticmethod
    def get_from_user():
        """Get credentials from ~/.eazyrent/credentials using EAZ_PROFILE or default."""
        profile = os.environ.get("EAZ_PROFILE", "default")
        credentials_path = Path.home() / ".eazyrent" / "credentials"

        if not credentials_path.exists():
            logger.warning("Credentials file not found.")
            return None

        config = ConfigParser()
        config.read(credentials_path)

        if profile not in config:
            logger.warning(f"Profile [{profile}] not found in credentials.")
            return None

        section = config[profile]

        try:
            if "JSON_KEY" in section:
                json_raw = section["JSON_KEY"]
                json_path = Path(json_raw).expanduser()
                if json_path.exists():
                    with open(json_path) as f:
                        data = json.load(f)
                else:
                    data = json.loads(json_raw)
                return JsonKey(**data)

            elif "API_KEY" in section:
                return ApiKey(token=SecretStr(section["API_KEY"]))

            elif "ACCESS_KEY_ID" in section and "SECRET_ACCESS_KEY" in section:
                return ClientCredentials(
                    key=section["ACCESS_KEY_ID"],
                    secret=SecretStr(section["SECRET_ACCESS_KEY"]),
                )
        except Exception as e:
            logger.error(f"Invalid credentials in profile [{profile}]: {e}")
        return None

    @classmethod
    def resolve(cls):
        """Resolve credentials from environment or user config file."""
        credentials = cls.get_credentials_from_environment()
        if credentials:
            logger.info("Credentials loaded from environment.")
            return credentials

        credentials = cls.get_from_user()
        if credentials:
            logger.info("Credentials loaded from ~/.eazyrent/credentials.")
            return credentials
        return None

    @classmethod
    def authenticate(cls) -> Tuple[Literal["token", "bearer"], str] | None:
        credentials = cls.resolve()
        if credentials:
            if isinstance(credentials, ApiKey):
                return "token", credentials.token.get_secret_value()
            elif isinstance(credentials, JsonKey):
                return "bearer", OAuth.jwt_bearer_client_credentials(credentials)
            elif isinstance(credentials, ClientCredentials):
                return "bearer", OAuth.client_credentials_flow(credentials)
            else:
                raise ValueError("Invalid auth method.")
        logger.info("No valid credentials found.")
        return None
