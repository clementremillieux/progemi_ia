"""User schemas"""

import base64

from enum import Enum

from typing import Annotated, List, Optional

from bson import Binary

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    PlainValidator,
)

from beanie import Document

from beanie.odm.fields import PydanticObjectId

from app.progemi_api.schemas import PackProgemi

from app.proposal_object.schemas import ProposalWithPolygonAndValidation

from app.proposal_object.proposal_validate_results import ValidationReport


def _bson_from_b64(v: str | bytes | Binary) -> Binary:
    """Convert a base64 encoded string or bytes to a BSON Binary object."""

    if isinstance(v, Binary):
        return v

    if isinstance(v, bytes):
        return Binary(v)

    if isinstance(v, str):
        v = v.encode()

    try:
        return Binary(base64.b64decode(v))

    except Exception as exc:
        raise ValueError("Invalid base64 data") from exc


def _b64_from_bson(v: Binary, _info) -> str:
    return base64.b64encode(bytes(v)).decode()


BsonBinary = Annotated[
    Binary,
    PlainValidator(_bson_from_b64),
    PlainSerializer(_b64_from_bson, return_type=str),
    Field(
        description="Binary data encoded as base64 string",
        json_schema_extra={"type": "string", "format": "byte"},
    ),
]


class ProposalFile(Document):
    """Proposal file schema."""

    id: Optional[PydanticObjectId] = Field(
        default_factory=PydanticObjectId, alias="_id"
    )

    pdf_content: BsonBinary

    class Settings:
        """Settings for the ProposalFile collection."""

        name = "proposals"

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ProposalStatus(str, Enum):
    """Enumeration for proposal status."""

    PENDING = "pending"

    PROCESSED = "processed"

    ACCEPTED = "accepted"


class ProposalInfos(BaseModel):
    """Proposal information schema."""

    title: str = Field(..., description="Title of the proposal")

    status: ProposalStatus = Field(
        default=ProposalStatus.PENDING,
        description="Status of the proposal",
    )

    pdf_id: Optional[PydanticObjectId] = Field(
        default=None,
        description="ID of the PDF file associated with the proposal",
    )

    packs: List[str] = Field(
        ...,
        description="List of pack names associated with the proposal",
    )


class Proposal(ProposalInfos):
    """Proposal schema."""

    proposal_str: Optional[str] = Field(
        default=None,
        description="String representation of the proposal from OCR",
    )

    extracted_object: Optional[ProposalWithPolygonAndValidation] = Field(
        default=None,
        description="Extracted object from the proposal, containing structured data",
    )

    validation_object: Optional[ValidationReport] = Field(
        default=None,
        description="Validation report for the proposal, containing validation results",
    )


class Project(BaseModel):
    """Project schema."""

    name: str = Field(..., description="Name of the project")

    proposals: List[Proposal] = Field(
        default_factory=list,
        description="List of proposals associated with the project",
    )

    project_packs: List[PackProgemi] = Field(
        ...,
        description="List of pack names associated with the project",
    )

    is_pack_to_choose: bool = Field(
        default=True,
        description="Indicates if the project has packs to choose from",
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class User(Document):
    """User schema."""

    id: Optional[PydanticObjectId] = Field(
        default_factory=PydanticObjectId, alias="_id"
    )

    name: str = Field(..., description="Name of the user")

    user_id: str = Field(..., description="ID of the user")

    user_packs: List[PackProgemi] = Field(
        ...,
        description="List of all pack names associated with the user",
    )

    projects: List[Project] = Field(
        default_factory=list, description="List of projects associated with the user"
    )

    class Settings:
        """Settings for the User collection."""

        name = "users"


class NewUserInput(BaseModel):
    """Parameters for creating a new user."""

    user_name: str = Field(..., description="Name of the new user")

    user_id: str = Field(..., description="ID of the new user")

    user_packs: List[PackProgemi] = Field(
        ...,
        description="List of pack names associated with the new user",
    )


class GetUsersPacksNamesOutput(BaseModel):
    """Output schema for user packs names."""

    packs_names: List[str] = Field(
        ...,
        description="List of pack names associated with the user",
    )


class NewProjectInput(BaseModel):
    """Parameters for creating a new project."""

    project_name: str = Field(..., description="Name of the new project")

    packs: List[str] = Field(
        ..., description="List of pack names associated with the project"
    )


class DeleteProjectInput(BaseModel):
    """Parameters for deleting a project."""

    project_name: str = Field(..., description="Name of the project to delete")


class UploadProposalInput(BaseModel):
    """Parameters for uploading a proposal."""

    project_name: str = Field(..., description="Name of the project")


class GetProposalInput(BaseModel):
    """Parameters for getting a proposal."""

    project_name: str = Field(..., description="Name of the project")

    proposal_id: PydanticObjectId = Field(
        ...,
        description="ID of the proposal to retrieve",
    )


class GetAllProposalsInput(BaseModel):
    """Parameters for getting all proposals of a project."""

    project_name: str = Field(..., description="Name of the project")


class DeleteProposalInput(BaseModel):
    """Parameters for deleting a proposal."""

    project_name: str = Field(..., description="Name of the project")

    proposal_title: str = Field(
        ...,
        description="Title of the proposal to delete",
    )


class UserProjectOutput(BaseModel):
    """Output schema for user projects."""

    project_name: str = Field(
        ...,
        description="Name of the project associated with the user",
    )

    packs_names: List[str] = Field(
        ...,
        description="List of pack names associated with the project",
    )

    is_pack_to_choose: bool = Field(
        ...,
        description="Indicates if the project has packs to choose from",
    )


class GetProjectPacksInput(BaseModel):
    """Parameters for getting all packs of a project."""

    project_name: str = Field(..., description="Name of the project")


class UpdateProjectPacksInput(BaseModel):
    """Parameters for updating the project packs."""

    project_name: str = Field(..., description="Name of the project")

    packs_name: List[str] = Field(
        ..., description="List of new pack names associated with the project"
    )


class GetProposalExtractedObjectInput(BaseModel):
    """Parameters for getting a structured proposal object."""

    project_name: str = Field(..., description="Name of the project")

    proposal_title: str = Field(
        ...,
        description="Title of the proposal to retrieve",
    )


class SetProposalExtractedObjectInput(BaseModel):
    """Parameters for setting a structured proposal object."""

    project_name: str = Field(..., description="Name of the project")

    title: str = Field(
        ...,
        description="Title of the proposal to update",
    )

    extracted_object: ProposalWithPolygonAndValidation = Field(
        ...,
        description="Structured data extracted from the proposal",
    )


class CreateProposalObjectInput(BaseModel):
    """Parameters for getting a structured proposal object."""

    project_name: str = Field(..., description="Name of the project")

    proposal_title: str = Field(
        ...,
        description="Title of the proposal to analyze and structure",
    )


class GetProposalObjectValidationInput(BaseModel):
    """Parameters for getting a proposal object validation."""

    project_name: str = Field(..., description="Name of the project")

    proposal_title: str = Field(
        ...,
        description="Title of the proposal to analyze and structure",
    )


class CreateProposalObjectValidationInput(BaseModel):
    """Parameters for creating a proposal object validation."""

    project_name: str = Field(..., description="Name of the project")

    proposal_title: str = Field(
        ...,
        description="Title of the proposal to analyze and structure",
    )
