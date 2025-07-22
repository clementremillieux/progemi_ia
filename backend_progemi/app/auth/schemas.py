"""Authentication and authorization schemas for user management."""

from pydantic import BaseModel, Field


class ConnectedUser(BaseModel):
    """Schema for the currently connected user."""

    user_id: str = Field(..., description="ID of the connected user")

    token: str

    ip_client: str = Field(
        ...,
        description="IP address of the client making the request",
    )

    idholding: int = Field(
        ...,
        description="ID of the holding associated with the user",
    )

    idsociete: int = Field(
        ...,
        description="ID of the company associated with the user",
    )

    idagence: int = Field(
        ...,
        description="ID of the agency associated with the user",
    )
