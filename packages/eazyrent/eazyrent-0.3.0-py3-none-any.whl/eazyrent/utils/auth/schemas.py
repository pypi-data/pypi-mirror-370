from datetime import datetime

from pydantic import BaseModel, Field, SecretStr


class ClientCredentials(BaseModel):
    key: str
    secret: SecretStr


class ApiKey(BaseModel):
    token: SecretStr


class JsonKey(BaseModel):
    type: str
    key_id: str = Field(alias="keyId")
    key: SecretStr = Field()
    expiration_date: datetime = Field(alias="expirationDate")
    user_id: str = Field(alias="userId")
