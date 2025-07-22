"""Users routes"""

import io

from typing import List

from fastapi import (
    Depends,
    File,
    Form,
    Response,
    APIRouter,
    UploadFile,
)

from fastapi.responses import StreamingResponse

from app.auth.auth import verify_token

from app.auth.schemas import ConnectedUser

from app.progemi_api.schemas import PackProgemi

from app.user.schemas import (
    CreateProposalObjectInput,
    CreateProposalObjectValidationInput,
    DeleteProjectInput,
    DeleteProposalInput,
    GetAllProposalsInput,
    GetProjectPacksInput,
    GetProposalExtractedObjectInput,
    GetProposalInput,
    GetProposalObjectValidationInput,
    GetUsersPacksNamesOutput,
    NewProjectInput,
    NewUserInput,
    ProposalFile,
    ProposalInfos,
    SetProposalExtractedObjectInput,
    UpdateProjectPacksInput,
    UploadProposalInput,
    User,
    UserProjectOutput,
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
async def new_user(new_user_input: NewUserInput, _=Depends(verify_token)) -> Response:
    """
    Create a new user with the provided user ID.
    """

    await UserHandler().create_user(new_user_params=new_user_input)

    return Response(
        status_code=200,
        content=f"User {new_user_input.user_id} [{new_user_input.user_name}] created successfully",
    )


@router.get(
    "/get_user",
    response_model=User,
    responses={
        404: {"description": "User does not exist"},
    },
)
async def get_user(connected_user: ConnectedUser = Depends(verify_token)) -> User:
    """
    Retrieve user information based on the provided user ID.
    """

    user = await UserHandler().get_user(connected_user=connected_user)

    return user


@router.get(
    "/get_user_packs_names",
    response_model=GetUsersPacksNamesOutput,
    responses={
        404: {"description": "User does not exist"},
    },
)
async def get_user_packs_names(
    connected_user: ConnectedUser = Depends(verify_token),
) -> GetUsersPacksNamesOutput:
    """
    Retrieve user information based on the provided user ID.
    """

    user_packs_names: List[str] = await UserHandler().get_user_packs_names(
        connected_user=connected_user
    )

    return GetUsersPacksNamesOutput(packs_names=user_packs_names)


@router.post("/delete_user")
async def delete_user(
    connected_user: ConnectedUser = Depends(verify_token),
) -> Response:
    """
    Delete a user based on the provided user ID.
    """

    await UserHandler().delete_user(connected_user=connected_user)

    return Response(
        status_code=200,
        content=f"User {connected_user.user_id} deleted successfully",
    )


@router.post("/new_project")
async def new_project(
    new_project_input: NewProjectInput,
    connected_user: ConnectedUser = Depends(verify_token),
) -> Response:
    """
    Create a new project for the given user.
    """

    await UserHandler().create_new_project(
        new_project_input=new_project_input,
        connected_user=connected_user,
    )

    return Response(
        status_code=200,
        content=f"Project {new_project_input.project_name} created successfully for user {connected_user.user_id}",
    )


@router.post("/delete_project")
async def delete_project(
    delete_project_input: DeleteProjectInput,
    connected_user: ConnectedUser = Depends(verify_token),
) -> Response:
    """
    Delete a project for the given user.
    """

    await UserHandler().delete_project(
        delete_project_input=delete_project_input,
        connected_user=connected_user,
    )

    return Response(
        status_code=200,
        content=f"Project {delete_project_input.project_name} deleted successfully for user {connected_user.user_id}",
    )


@router.post("/get_all_projects")
async def get_all_projects(
    connected_user: ConnectedUser = Depends(verify_token),
) -> List[UserProjectOutput]:
    """
    Retrieve all projects name associated with a user.
    """

    await UserHandler().run_delta_projects(connected_user=connected_user)

    projects = await UserHandler().get_all_user_projects(connected_user=connected_user)

    return [
        UserProjectOutput(
            project_name=project.name,
            packs_names=[pack.libellelot for pack in project.project_packs],
            is_pack_to_choose=project.is_pack_to_choose,
        )
        for project in projects
    ]


@router.post("/upload_proposal")
async def upload_proposal(
    project_name: str = Form(...),
    file: UploadFile = File(...),
    connected_user: ConnectedUser = Depends(verify_token),
) -> Response:
    """
    Upload a proposal file for the given user & project.
    """

    await UserHandler().upload_proposal_to_project(
        upload_proposal_input=UploadProposalInput(
            project_name=project_name,
        ),
        file=file,
        connected_user=connected_user,
    )

    return Response(
        status_code=200,
        content=f"File {file.filename} uploaded successfully for user {connected_user.user_id}",
    )


@router.post("/get_proposal")
async def get_proposal(
    get_proposal_input: GetProposalInput,
    _=Depends(verify_token),
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
        media_type="application/pdf",
        headers=headers,
    )


@router.post("/delete_proposal")
async def delete_proposal(
    delete_proposal_input: DeleteProposalInput,
    connected_user: ConnectedUser = Depends(verify_token),
) -> Response:
    """
    Delete a proposal for the given user & project.
    """

    await UserHandler().delete_proposal_by_title(
        delete_proposal_input=delete_proposal_input,
        connected_user=connected_user,
    )

    return Response(
        status_code=200,
        content=f"Proposal {delete_proposal_input.proposal_title} deleted successfully for user {connected_user.user_id} in project {delete_proposal_input.project_name}",
    )


@router.post("/get_all_proposals_infos")
async def get_all_proposals(
    get_all_proposals_input: GetAllProposalsInput,
    connected_user: ConnectedUser = Depends(verify_token),
) -> List[ProposalInfos]:
    """
    Retrieve all proposals associated with a project for a user.
    """

    proposals = await UserHandler().get_all_user_project_proposal_infos(
        get_all_proposals_input=get_all_proposals_input,
        connected_user=connected_user,
    )

    return proposals


@router.get("/get_project_packs")
async def get_project_packs(
    get_project_packs_input: GetProjectPacksInput,
    connected_user: ConnectedUser = Depends(verify_token),
) -> List[PackProgemi]:
    """
    Retrieve all packs associated with a project for a user.
    """

    packs = await UserHandler().get_project_packs(
        get_project_packs_input=get_project_packs_input, connected_user=connected_user
    )

    return packs


@router.post("/get_project_packs_names")
async def get_project_packs_names(
    get_project_packs_input: GetProjectPacksInput,
    connected_user: ConnectedUser = Depends(verify_token),
) -> List[str]:
    """
    Retrieve all pack names associated with a project for a user.
    """

    packs = await UserHandler().get_project_packs(
        get_project_packs_input=get_project_packs_input, connected_user=connected_user
    )

    return [pack.libellelot for pack in packs]


@router.post("/update_project_packs")
async def update_project_packs(
    update_project_packs_input: UpdateProjectPacksInput,
    connected_user: ConnectedUser = Depends(verify_token),
) -> Response:
    """
    Update the packs associated with a project for a user.
    """

    await UserHandler().update_project_packs(
        update_project_packs_input=update_project_packs_input,
        connected_user=connected_user,
    )

    return Response(
        status_code=200,
        content=f"Project {update_project_packs_input.project_name} packs updated successfully for user {connected_user.user_id}",
    )


@router.post("/get_proposal_extracted_object")
async def get_proposal_extracted_object(
    get_proposal_extracted_object_input: GetProposalExtractedObjectInput,
    connected_user: ConnectedUser = Depends(verify_token),
) -> ProposalWithPolygonAndValidation:
    """
    Retrieve the structured proposal object for a given proposal title.
    """

    extracted_object: ProposalWithPolygonAndValidation = (
        await UserHandler().get_proposal_extracted_object(
            get_proposal_extracted_object_input=get_proposal_extracted_object_input,
            connected_user=connected_user,
        )
    )

    return extracted_object


@router.post("/set_proposal_extracted_object")
async def set_proposal_extracted_object(
    set_proposal_extracted_object_input: SetProposalExtractedObjectInput,
    connected_user: ConnectedUser = Depends(verify_token),
) -> ProposalWithPolygonAndValidation:
    """
    Set the structured proposal object for a given proposal title.
    """

    proposal_validate_saved: ProposalWithPolygonAndValidation = (
        await UserHandler().set_proposal_extracted_object(
            set_proposal_extracted_object_input=set_proposal_extracted_object_input,
            connected_user=connected_user,
        )
    )

    return proposal_validate_saved


@router.post("/get_proposal_object")
async def get_proposal_object(
    get_proposal_object_input: CreateProposalObjectInput,
    connected_user: ConnectedUser = Depends(verify_token),
) -> ProposalWithPolygonAndValidation:
    """
    Retrieve a structured proposal object for a given proposal title.
    """

    proposal_object: ProposalWithPolygonAndValidation = (
        await UserHandler().create_proposal_object(
            create_proposal_object_input=get_proposal_object_input,
            connected_user=connected_user,
        )
    )

    return proposal_object


@router.post("/create_proposal_object_validation")
async def create_proposal_object_validation(
    create_proposal_object_validation_input: CreateProposalObjectValidationInput,
    connected_user: ConnectedUser = Depends(verify_token),
) -> ValidationReport:
    """
    Retrieve the validation report for a given proposal title.
    """

    validation_report: ValidationReport = (
        await UserHandler().create_proposal_object_validation(
            create_proposal_object_input=create_proposal_object_validation_input,
            connected_user=connected_user,
        )
    )

    return validation_report


@router.get("/get_proposal_object_validation")
async def get_proposal_object_validation(
    get_proposal_object_validation_input: GetProposalObjectValidationInput,
    connected_user: ConnectedUser = Depends(verify_token),
) -> ValidationReport:
    """
    Retrieve the validation report for a given proposal title.
    """

    validation_report: ValidationReport = (
        await UserHandler().get_proposal_validation_by_title(
            get_proposal_validation_input=get_proposal_object_validation_input,
            connected_user=connected_user,
        )
    )

    return validation_report
