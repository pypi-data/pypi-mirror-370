from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID
from maleo.soma.enums.token import TokenType
from maleo.soma.types.base import (
    OptionalInteger,
    OptionalListOfStrings,
    OptionalString,
    OptionalUUID,
)


class CredentialPayload(BaseModel):
    iss: OptionalString = Field(None, description="Token's issuer")
    sub: str = Field(..., description="Token's subject")
    sr: str = Field(..., description="System role")
    u_i: int = Field(..., description="user's id")
    u_uu: UUID = Field(..., description="user's uuid")
    u_u: str = Field(..., description="user's username")
    u_e: str = Field(..., description="user's email")
    u_ut: str = Field(..., description="user's type")
    o_i: OptionalInteger = Field(None, description="Organization's id")
    o_uu: OptionalUUID = Field(None, description="Organization's uuid")
    o_k: OptionalString = Field(None, description="Organization's key")
    o_ot: OptionalString = Field(None, description="Organization's type")
    uor: OptionalListOfStrings = Field(None, description="User Organization Role")


class TimestampPayload(BaseModel):
    iat_dt: datetime = Field(..., description="Issued at (datetime)")
    iat: int = Field(..., description="Issued at (integer)")
    exp_dt: datetime = Field(..., description="Expired at (datetime)")
    exp: int = Field(..., description="Expired at (integer)")


class Payload(TimestampPayload, CredentialPayload):
    pass


class AuthenticationToken(BaseModel):
    type: TokenType = Field(..., description="Token's type")
    payload: Payload = Field(..., description="Token's payload")
