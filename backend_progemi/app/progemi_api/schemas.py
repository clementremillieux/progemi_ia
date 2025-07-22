"""PROGEMI API Schemas."""

from pydantic import BaseModel, Field


class PackProgemi(BaseModel):
    """Schema for the packs retrieved from the Progemi API."""

    codelot: str = Field(
        ...,
        description="Code of the pack",
    )

    idlot: int = Field(
        ...,
        description="ID of the pack",
    )

    libellelot: str = Field(
        ...,
        description="Name of the pack",
    )


class ProjectProgemi(BaseModel):
    """Schema for the project retrieved from the Progemi API."""

    idprojet: int = Field(
        ...,
        description="ID of the project",
    )

    codeprojet: str = Field(
        ...,
        description="Code of the project",
    )

    designationprojet: str = Field(
        ...,
        description="Name of the project",
    )

    nomprospect: str = Field(
        ...,
        description="Name of the prospect associated with the project",
    )
