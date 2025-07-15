"""Users routes"""

import io

from typing import List

from pydantic import EmailStr

from fastapi import (
    File,
    Form,
    Response,
    APIRouter,
    UploadFile,
)

from fastapi.responses import StreamingResponse

from app.user.schemas import (
    CreateProposalObjectInput,
    CreateProposalObjectValidationInput,
    DeleteProjectInput,
    DeleteProposalInput,
    DeleteUserInput,
    GetAllProjectsInput,
    GetAllProposalsInput,
    GetProjectPacksInput,
    GetProposalExtractedObjectInput,
    GetProposalInput,
    GetProposalObjectValidationInput,
    GetUserInput,
    NewProjectInput,
    NewUserInput,
    ProposalFile,
    ProposalInfos,
    SetProposalExtractedObjectInput,
    UpdateProjectPacksInput,
    UploadProposalInput,
    User,
)

from app.user.user_handler import UserHandler

from app.proposal_object.schemas import ProposalWithPolygonAndValidation

from app.proposal_object.proposal_validate_results import ValidationReport


router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post(
    "/new_user",
    responses={
        409: {"description": "User already exists"},
    },
)
async def new_user(new_user_input: NewUserInput) -> Response:
    """
    Create a new user with the provided user ID.
    """

    await UserHandler().create_user(new_user_input)

    return Response(
        status_code=200,
        content=f"User {new_user_input.user_email} [{new_user_input.user_name}] created successfully",
    )


@router.get(
    "/get_user",
    response_model=User,
    responses={
        404: {"description": "User does not exist"},
    },
)
async def get_user(get_user_input: GetUserInput) -> User:
    """
    Retrieve user information based on the provided user ID.
    """

    user = await UserHandler().get_user(get_user_input)

    return user


@router.post("/delete_user")
async def delete_user(delete_user_input: DeleteUserInput) -> Response:
    """
    Delete a user based on the provided user ID.
    """

    await UserHandler().delete_user(delete_user_input)

    return Response(
        status_code=200,
        content=f"User {delete_user_input.user_email} deleted successfully",
    )


@router.post("/new_project")
async def new_project(
    new_project_input: NewProjectInput,
) -> Response:
    """
    Create a new project for the given user.
    """

    await UserHandler().create_new_project(
        new_project_input=new_project_input,
    )

    return Response(
        status_code=200,
        content=f"Project {new_project_input.project_name} created successfully for user {new_project_input.user_email}",
    )


@router.post("/delete_project")
async def delete_project(
    delete_project_input: DeleteProjectInput,
) -> Response:
    """
    Delete a project for the given user.
    """

    await UserHandler().delete_project(
        delete_project_input=delete_project_input,
    )

    return Response(
        status_code=200,
        content=f"Project {delete_project_input.project_name} deleted successfully for user {delete_project_input.user_email}",
    )


@router.post("/get_all_projects")
async def get_all_projects(
    get_all_projects_input: GetAllProjectsInput,
) -> List[str]:
    """
    Retrieve all projects name associated with a user.
    """
    

    projects = await UserHandler().get_all_projects_name(get_all_projects_input)

    return projects


@router.post("/upload_proposal")
async def upload_proposal(
    user_email: EmailStr = Form(...),
    project_name: str = Form(...),
    file: UploadFile = File(...),
) -> Response:
    """
    Upload a proposal file for the given user & project.
    """

    await UserHandler().upload_proposal_to_project(
        upload_proposal_input=UploadProposalInput(
            user_email=user_email,
            project_name=project_name,
        ),
        file=file,
    )

    return Response(
        status_code=200,
        content=f"File {file.filename} uploaded successfully for user {user_email}",
    )


@router.post("/get_proposal")
async def get_proposal(
    get_proposal_input: GetProposalInput,
) -> StreamingResponse:
    """
    Return a proposal file for the given user & project.
    """

    proposal_doc: ProposalFile = await UserHandler().get_proposal_by_id(
        get_proposal_input
    )

    file_like = io.BytesIO(bytes(proposal_doc.pdf_content))

    headers = {"Content-Disposition": 'inline; filename="proposal.pdf"'}

    return StreamingResponse(
        file_like,
        media_type="application/pdf",  # important pour l’aperçu
        headers=headers,
    )


@router.post("/delete_proposal")
async def delete_proposal(
    delete_proposal_input: DeleteProposalInput,
) -> Response:
    """
    Delete a proposal for the given user & project.
    """

    await UserHandler().delete_proposal_by_title(
        delete_proposal_input=delete_proposal_input,
    )

    return Response(
        status_code=200,
        content=f"Proposal {delete_proposal_input.proposal_title} deleted successfully for user {delete_proposal_input.user_email} in project {delete_proposal_input.project_name}",
    )


@router.post("/get_all_proposals_infos")
async def get_all_proposals(
    get_all_proposals_input: GetAllProposalsInput,
) -> List[ProposalInfos]:
    """
    Retrieve all proposals associated with a project for a user.
    """

    proposals = await UserHandler().get_all_user_project_proposal_infos(
        get_all_proposals_input=get_all_proposals_input
    )

    return proposals


@router.get("/get_project_packs")
async def get_project_packs(get_project_packs_input: GetProjectPacksInput) -> List[str]:
    """
    Retrieve all packs associated with a project for a user.
    """

    packs = await UserHandler().get_project_packs(get_project_packs_input)

    return packs


@router.post("/update_project_packs")
async def update_project_packs(
    update_project_packs_input: UpdateProjectPacksInput,
) -> Response:
    """
    Update the packs associated with a project for a user.
    """

    await UserHandler().update_project_packs(
        update_project_packs_input=update_project_packs_input,
    )

    return Response(
        status_code=200,
        content=f"Project {update_project_packs_input.project_name} packs updated successfully for user {update_project_packs_input.user_email}",
    )


@router.post("/get_proposal_extracted_object")
async def get_proposal_extracted_object(
    get_proposal_extracted_object_input: GetProposalExtractedObjectInput,
) -> ProposalWithPolygonAndValidation:
    """
    Retrieve the structured proposal object for a given proposal title.
    """

    extracted_object: ProposalWithPolygonAndValidation = (
        await UserHandler().get_proposal_extracted_object(
            get_proposal_extracted_object_input
        )
    )

    return extracted_object


@router.post("/set_proposal_extracted_object")
async def set_proposal_extracted_object(
    set_proposal_extracted_object_input: SetProposalExtractedObjectInput,
) -> ProposalWithPolygonAndValidation:
    """
    Set the structured proposal object for a given proposal title.
    """

    proposal_validate_saved: ProposalWithPolygonAndValidation = (
        await UserHandler().set_proposal_extracted_object(
            set_proposal_extracted_object_input=set_proposal_extracted_object_input,
        )
    )

    return proposal_validate_saved


@router.post("/get_proposal_object")
async def get_proposal_object(
    get_proposal_object_input: CreateProposalObjectInput,
) -> ProposalWithPolygonAndValidation:
    """
    Retrieve a structured proposal object for a given proposal title.
    """

    proposal_object: ProposalWithPolygonAndValidation = (
        await UserHandler().create_proposal_object(
            create_proposal_object_input=get_proposal_object_input
        )
    )

    return proposal_object


@router.post("/create_proposal_object_validation")
async def create_proposal_object_validation(
    create_proposal_object_validation_input: CreateProposalObjectValidationInput,
) -> ValidationReport:
    """
    Retrieve the validation report for a given proposal title.
    """

    validation_report: ValidationReport = (
        await UserHandler().create_proposal_object_validation(
            create_proposal_object_input=create_proposal_object_validation_input
        )
    )

    return validation_report


@router.get("/get_proposal_object_validation")
async def get_proposal_object_validation(
    get_proposal_object_validation_input: GetProposalObjectValidationInput,
) -> ValidationReport:
    """
    Retrieve the validation report for a given proposal title.
    """

    validation_report: ValidationReport = (
        await UserHandler().get_proposal_validation_by_title(
            get_proposal_validation_input=get_proposal_object_validation_input
        )
    )

    return validation_report
