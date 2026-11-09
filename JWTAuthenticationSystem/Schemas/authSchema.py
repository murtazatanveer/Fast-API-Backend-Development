from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class SignupRequest(CamelModel):
    username: str = Field(min_length=8, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("username", mode="before")
    @classmethod
    def validateUsername(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Username must be a string")
        username = value.strip()
        if len(username) < 8:
            raise ValueError("Username must be at least 8 characters long")
        if not any(char.isupper() for char in username):
            raise ValueError("Username must contain at least one uppercase letter")
        if not any(char.isdigit() for char in username):
            raise ValueError("Username must contain at least one digit")
        if not any(not char.isalnum() for char in username):
            raise ValueError("Username must contain at least one special character")
        return username


class LoginRequest(CamelModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=72)


class VerifyLoginRequest(CamelModel):
    username: str = Field(min_length=1, max_length=50)
    otp: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class AccessTokenPayload(CamelModel):
    user_id: UUID
    jti: str
    exp: int
    iat: int | None = None
