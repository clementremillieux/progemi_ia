"""User handler module"""

from typing import List, Optional

from fastapi import UploadFile

from pymongo.errors import DuplicateKeyError

from beanie.odm.fields import PydanticObjectId

from app.user.exception import (
    FileNameMissing,
    NoPacksInProject,
    ProjectNotFound,
    ProposalNotExtracted,
    ProposalNotFound,
    ProposalValidationNotCreated,
    UserAlreadyExists,
    UserNotExists,
)

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
    NewProjectInput,
    NewUserInput,
    Project,
    Proposal,
    ProposalFile,
    ProposalInfos,
    ProposalStatus,
    SetProposalExtractedObjectInput,
    UpdateProjectPacksInput,
    UploadProposalInput,
    User,
    GetUserInput,
)


from app.proposal_object.proposal_validate_results import (
    ValidationReport,
)

from app.proposal_object.proposal_handler import ProposalHandler

from app.proposal_object.schemas import ProposalWithPolygonAndValidation

from app.proposal_object.proposal_object_analyzer import ProposalObjectHandler

from config.logger_config import logger


class UserHandler:
    """User handler class to manage user-related operations."""

    def __init__(self):
        """Initialize the UserHandler"""

    def build_new_user(self, new_user_params: NewUserInput) -> User:
        """Build a new user object.

        Args:
            user_name (str): The name of the user.
            user_email (str): The email of the user.

        Returns:
            User: A User object with default values.
        """

        return User(
            name=new_user_params.user_name,
            email=new_user_params.user_email,
            projects=[],
        )

    async def create_user(self, new_user_params: NewUserInput) -> None:
        """Create a new user.

        Args:
            user_name (str): The name of the user.
            user_email (str): The email of the user.

        Returns:
            User: A User object with default values.

        Raises:
            UserAlreadyExists: If the user already exists.
            DuplicateKeyError: If there is a duplicate key error during insertion.
        """

        try:
            new_user: User = self.build_new_user(new_user_params)

            await new_user.insert()

        except DuplicateKeyError as e:
            logger.error("USER HANDLER => User %s already exists.", new_user.email)

            raise UserAlreadyExists() from e

    async def get_user(self, get_user_input: GetUserInput) -> User:
        """Get user by user_email.

        Args:
            get_user_input (GetUserInput): Input containing user_email to retrieve the user.
        Returns:
            User: The user object if found.
        Raises:
            UserNotExists: If the user does not exist.
        """

        user: Optional[User] = await User.find_one(
            User.email == get_user_input.user_email
        )

        if not user:
            logger.error(
                "USER HANDLER => User %s not found.", get_user_input.user_email
            )

            raise UserNotExists(user_email=get_user_input.user_email)

        logger.debug(
            "USER HANDLER => User %s retrieved successfully.", get_user_input.user_email
        )

        return user

    async def delete_user(self, delete_user_input: DeleteUserInput) -> None:
        """Delete user by user_email.

        Args:
            delete_user_input (DeleteUserInput): Input containing user_email to delete the user.
        Returns:
            None: If the user is deleted successfully.
        Raises:
            UserNotExists: If the user does not exist.
        """

        user: User = await self.get_user(
            get_user_input=GetUserInput(user_email=delete_user_input.user_email)
        )

        await user.delete()

        logger.debug(
            "USER HANDLER => User %s deleted successfully.",
            delete_user_input.user_email,
        )

    async def insert_proposal_file(self, file: UploadFile) -> Proposal:
        """Insert a proposal file into the database.

        Args:
            file (UploadFile): The proposal file to be inserted.

        Returns:
            Proposal: The inserted proposal object.

        Raises:
            FileNameMissing: If the file name is missing.
        """

        if not file.filename:
            logger.error("USER HANDLER => No file name provided for upload.")

            raise FileNameMissing()

        proposal_file = ProposalFile(pdf_content=await file.read())

        await proposal_file.insert()

        proposal = Proposal(
            title=file.filename, status=ProposalStatus.PENDING, pdf_id=proposal_file.id
        )

        return proposal

    async def get_proposal_file_by_id(
        self, proposal_id: PydanticObjectId
    ) -> ProposalFile:
        """Get a proposal file by its ID.

        Args:
            proposal_id (PydanticObjectId): The ID of the proposal file to retrieve.

        Returns:
            ProposalFile: The proposal file object if found.
        """

        proposal_file: Optional[ProposalFile] = await ProposalFile.get(proposal_id)

        if not proposal_file:
            logger.error(
                "USER HANDLER => Proposal file with ID %s not found.", proposal_id
            )

            raise ProposalNotFound(proposal_id=proposal_id)

        return proposal_file

    async def get_proposal_file_by_title(
        self, project: Project, proposal_title: str
    ) -> ProposalFile:
        """Get a proposal file by its title.

        Args:
            proposal_title (str): The title of the proposal file to retrieve.

        Returns:
            ProposalFile: The proposal file object if found.

        Raises:
            ProposalNotFound: If the proposal file is not found.
        """

        proposal: Proposal = self.get_proposal_by_title(
            project=project, title=proposal_title
        )

        if not proposal.pdf_id:
            logger.error(
                "USER HANDLER => Proposal %s does not have a PDF ID.",
                proposal_title,
            )

            raise ProposalNotFound(proposal_id=proposal.title)

        proposal_file: ProposalFile = await self.get_proposal_file_by_id(
            proposal_id=proposal.pdf_id
        )

        if not proposal_file:
            logger.error(
                "USER HANDLER => Proposal file with title %s not found.",
                proposal_title,
            )

            raise ProposalNotFound(proposal_id=proposal_title)

        return proposal_file

    async def delete_proposal_file(self, proposal_id: PydanticObjectId) -> None:
        """Delete a proposal file from the database.

        Args:
            proposal_id (PydanticObjectId): The ID of the proposal to delete.

        Returns:
            None: If the proposal file is deleted successfully.
        """

        if not proposal_id:
            logger.error("USER HANDLER => No PDF ID provided for deletion.")

            raise ProposalNotFound(proposal_id=str(proposal_id))

        proposal_file: ProposalFile = await self.get_proposal_file_by_id(
            proposal_id=str(proposal_id)
        )

        await proposal_file.delete()

        logger.debug(
            "USER HANDLER => Proposal file with ID %s deleted successfully.",
            str(proposal_id),
        )

    async def create_new_project(self, new_project_input: NewProjectInput) -> None:
        """Create a new project for a user.

        Args:
            user (User): The user object to which the project will be added.
            project_name (str): The name of the new project.

        Returns:
            None: If the project is created successfully.

        Raises:
            DuplicateKeyError: If a project with the same name already exists for the user.
        """

        user: User = await self.get_user(
            get_user_input=GetUserInput(user_email=new_project_input.user_email)
        )

        if any(proj.name == new_project_input.project_name for proj in user.projects):
            logger.error(
                "USER HANDLER => Project %s already exists for user %s.",
                new_project_input.project_name,
                user.email,
            )

            raise DuplicateKeyError(
                f"Project {new_project_input.project_name} already exists."
            )

        new_project = Project(
            name=new_project_input.project_name,
            proposals=[],
            packs=new_project_input.packs,
        )

        user.projects.append(new_project)

        await user.save()

        logger.debug(
            "USER HANDLER => Project %s created successfully for user %s.",
            new_project_input.project_name,
            user.email,
        )

    async def delete_project(self, delete_project_input: DeleteProjectInput) -> None:
        """Delete a project from a user's projects.

        Args:
            delete_project_input (DeleteProjectInput): Input containing user_email and project_name.

        Returns:
            None: If the project is deleted successfully.

        Raises:
            ProjectNotFound: If the project is not found for the user.
            UserNotExists: If the user does not exist.
        """

        user: User = await self.get_user(
            get_user_input=GetUserInput(user_email=delete_project_input.user_email)
        )

        project: Project = self.get_project_by_name(
            user=user, project_name=delete_project_input.project_name
        )

        user.projects.remove(project)

        await user.save()

        logger.debug(
            "USER HANDLER => Project %s deleted successfully for user %s.",
            delete_project_input.project_name,
            user.email,
        )

    async def get_all_projects_name(
        self, get_all_projects_input: GetAllProjectsInput
    ) -> List[str]:
        """Get the names of all projects for a user."""

        user: User = await self.get_user(
            get_user_input=GetUserInput(user_email=get_all_projects_input.user_email)
        )

        if not user.projects:
            logger.error("USER HANDLER => No projects found for user %s.", user.email)
            return []

        project_names: List[str] = [project.name for project in user.projects]

        logger.debug(
            "USER HANDLER => Retrieved projects names for user %s: %s.",
            user.email,
            project_names,
        )

        return project_names

    def get_project_by_name(self, user: User, project_name: str) -> Project:
        """Get a project by its name from a user.
        Args:
            user (User): The user object containing the projects.
            project_name (str): The name of the project to retrieve.
        Returns:
            Project: The project object if found.
        Raises:
            ProjectNotFound: If the project is not found for the user.
        """

        project = next(
            (proj for proj in user.projects if proj.name == project_name), None
        )

        if not project:
            logger.error(
                "USER HANDLER => Project %s not found for user %s.",
                project_name,
                user.email,
            )

            raise ProjectNotFound(project_name=project_name)

        return project

    def get_proposal_by_title(self, project: Project, title: str) -> Proposal:
        """Get a proposal by its title from a project.

        Args:
            project (Project): The project object containing the proposals.
            title (str): The title of the proposal to retrieve.

        Returns:
            Proposal: The proposal object if found.

        Raises:
            ProposalNotFound: If the proposal is not found in the project.
        """

        proposal = next(
            (prop for prop in project.proposals if prop.title == title), None
        )

        if not proposal:
            logger.error(
                "USER HANDLER => Proposal with title %s not found in project %s.",
                title,
                project.name,
            )

            raise ProposalNotFound(proposal_id=title)

        return proposal

    async def upload_proposal_to_project(
        self, upload_proposal_input: UploadProposalInput, file: UploadFile
    ) -> None:
        """Upload a proposal for a user to a project.

        Args:
            upload_proposal_input (UploadProposalInput): Input containing user_email and project_name.
            file (UploadFile): The file to be uploaded as a proposal.

        Returns:
            None: If the proposal is uploaded successfully.

        Raises:
            FileNameMissing: If the file name is missing.
            ProjectNotFound: If the project is not found for the user.
        """

        proposal: Proposal = await self.insert_proposal_file(file=file)

        user: User = await self.get_user(
            get_user_input=GetUserInput(user_email=upload_proposal_input.user_email)
        )

        project: Project = self.get_project_by_name(
            user=user, project_name=upload_proposal_input.project_name
        )

        project.proposals.append(proposal)

        await user.save()

        logger.debug(
            "USER HANDLER => Proposal %s uploaded for user %s in project %s.",
            file.filename,
            upload_proposal_input.user_email,
            upload_proposal_input.project_name,
        )

    async def delete_proposal_by_title(
        self, delete_proposal_input: DeleteProposalInput
    ) -> None:
        """Delete a proposal from a user's project and the database.

        Args:
            delete_proposal_input (DeleteProposalInput): Input containing user_email, project_name, and proposal_id.

        Returns:
            None: If the proposal is deleted successfully.

        Raises:
            ProjectNotFound: If the project is not found for the user.
            UserNotExists: If the user does not exist.
        """

        user: User = await self.get_user(
            get_user_input=GetUserInput(user_email=delete_proposal_input.user_email)
        )

        project: Project = self.get_project_by_name(
            user=user, project_name=delete_proposal_input.project_name
        )

        proposal: Proposal = self.get_proposal_by_title(
            project=project, title=delete_proposal_input.proposal_title
        )

        project.proposals.remove(proposal)

        await self.delete_proposal_file(proposal_id=proposal.pdf_id)

        await user.save()

        logger.debug(
            "USER HANDLER => Proposal with ID %s deleted from user %s in project %s.",
            proposal.pdf_id,
            delete_proposal_input.user_email,
            delete_proposal_input.project_name,
        )

    async def get_proposal_by_id(
        self, get_proposal_input: GetProposalInput
    ) -> ProposalFile:
        """Get a proposal file by its ID.

        Args:
            get_proposal_input (GetProposalInput): Input containing user_email and proposal_id.

        Returns:
            ProposalFile: The proposal file object if found.

        Raises:
            UserNotExists: If the user does not exist.
        """

        proposal_file: ProposalFile = await self.get_proposal_file_by_id(
            proposal_id=get_proposal_input.proposal_id
        )

        return proposal_file

    async def get_all_user_project_proposal_infos(
        self, get_all_proposals_input: GetAllProposalsInput
    ) -> List[ProposalInfos]:
        """Get all proposals for a user's projects.

        Args:
            get_all_proposals_input (GetAllProposalsInput): Input containing user_email and project_name.

        Returns:
            list[Proposal]: A list of proposals for the user's projects.
        """

        user: User = await self.get_user(
            get_user_input=GetUserInput(user_email=get_all_proposals_input.user_email)
        )

        project = self.get_project_by_name(
            user=user, project_name=get_all_proposals_input.project_name
        )

        return [
            ProposalInfos(**proposal.model_dump()) for proposal in project.proposals
        ]

    async def get_all_user_project_proposal_files(
        self, get_all_proposals_input: GetAllProposalsInput
    ) -> List[ProposalFile]:
        """Get all proposal files for a user's projects.

        Args:
            get_all_proposals_input (GetAllProposalsInput): Input containing user_email and project_name.

        Returns:
            list[ProposalFile]: A list of proposal files for the user's projects.
        """

        user: User = await self.get_user(
            get_user_input=GetUserInput(user_email=get_all_proposals_input.user_email)
        )

        project = self.get_project_by_name(
            user=user, project_name=get_all_proposals_input.project_name
        )

        proposal_project_ids: List[PydanticObjectId] = [
            proposal.pdf_id for proposal in project.proposals if proposal.pdf_id
        ]

        proposal_files: List[ProposalFile] = []

        for proposal_id in proposal_project_ids:
            proposal_file: ProposalFile = await self.get_proposal_file_by_id(
                proposal_id=proposal_id
            )

            proposal_files.append(proposal_file)

        return proposal_files

    async def get_project_packs(
        self, get_project_packs_input: GetProjectPacksInput
    ) -> List[str]:
        """Get all packs associated with a project for a user.

        Args:
            get_project_packs_input (GetProjectPacksInput): Input containing user_email and project_name.

        Returns:
            List[str]: A list of pack names associated with the project.

        Raises:
            UserNotExists: If the user does not exist.
            ProjectNotFound: If the project is not found for the user.
        """

        user: User = await self.get_user(
            get_user_input=GetUserInput(user_email=get_project_packs_input.user_email)
        )

        project: Project = self.get_project_by_name(
            user=user, project_name=get_project_packs_input.project_name
        )

        return project.packs

    async def update_project_packs(
        self, update_project_packs_input: UpdateProjectPacksInput
    ) -> None:
        """Update the packs associated with a project for a user.

        Args:
            update_project_packs_input (UpdateProjectPacksInput): Input containing user_email, project_name, and packs.
        """

        user: User = await self.get_user(
            get_user_input=GetUserInput(
                user_email=update_project_packs_input.user_email
            )
        )

        project: Project = self.get_project_by_name(
            user=user, project_name=update_project_packs_input.project_name
        )

        project.packs = update_project_packs_input.packs

        await user.save()

        logger.debug(
            "USER HANDLER => Packs updated for project %s of user %s.",
            update_project_packs_input.project_name,
            update_project_packs_input.user_email,
        )

    async def get_proposal_extracted_object(
        self, get_proposal_extracted_object_input: GetProposalExtractedObjectInput
    ) -> ProposalWithPolygonAndValidation:
        """Get the extracted object from a proposal.

        Args:
            get_proposal_extracted_object_input (GetProposalExtractedObjectInput): Input containing user_email, project_name, and title.

        Returns:
            ProposalWithPolygonAndValidation: The extracted object from the proposal.
        """

        user: User = await self.get_user(
            get_user_input=GetUserInput(
                user_email=get_proposal_extracted_object_input.user_email
            )
        )

        project: Project = self.get_project_by_name(
            user=user, project_name=get_proposal_extracted_object_input.project_name
        )

        proposal: Proposal = self.get_proposal_by_title(
            project=project, title=get_proposal_extracted_object_input.proposal_title
        )

        if not proposal.extracted_object:
            logger.error(
                "USER HANDLER => Proposal %s has not been extracted.",
                get_proposal_extracted_object_input.proposal_title,
            )

            raise ProposalNotExtracted(proposal_title=proposal.title)

        return proposal.extracted_object

    async def set_proposal_extracted_object(
        self, set_proposal_extracted_object_input: SetProposalExtractedObjectInput
    ) -> ProposalWithPolygonAndValidation:
        """Set the extracted object for a proposal.

        Args:
            set_proposal_extracted_object_input (SetProposalExtractedObjectInput): Input containing user_email, project_name, title, and extracted_object.
        Returns:
            None: If the extracted object is set successfully.
        """

        logger.debug(
            "USER HANDLER => Setting extracted object for proposal %s in project %s of user %s.",
            set_proposal_extracted_object_input.title,
            set_proposal_extracted_object_input.project_name,
            set_proposal_extracted_object_input.user_email,
        )

        user: User = await self.get_user(
            get_user_input=GetUserInput(
                user_email=set_proposal_extracted_object_input.user_email
            )
        )

        logger.debug(
            "USER HANDLER => User %s retrieved successfully.",
            user.email,
        )

        project: Project = self.get_project_by_name(
            user=user, project_name=set_proposal_extracted_object_input.project_name
        )

        logger.debug(
            "USER HANDLER => Project %s retrieved successfully for user %s.",
            project.name,
            user.email,
        )

        proposal_extracted_object, report = ProposalObjectHandler(
            proposal_object=set_proposal_extracted_object_input.extracted_object
        ).validate_proposal_object()

        await self.set_proposal_validation_by_title(
            project=project,
            proposal_title=set_proposal_extracted_object_input.title,
            validation_report=report,
        )

        await self.set_proposal_object_to_project(
            project=project,
            proposal_object=proposal_extracted_object,
            proposal_title=set_proposal_extracted_object_input.title,
        )

        logger.debug(
            "USER HANDLER => Extracted object set for proposal %s in project %s of user %s.",
            set_proposal_extracted_object_input.title,
            set_proposal_extracted_object_input.project_name,
            set_proposal_extracted_object_input.user_email,
        )

        await user.save()

        logger.debug("%s", proposal_extracted_object.model_dump_json(indent=2))

        return proposal_extracted_object

    async def set_proposal_object_to_project(
        self,
        project: Project,
        proposal_object: ProposalWithPolygonAndValidation,
        proposal_title: str,
    ) -> None:
        """Set the proposal object for a project.

        Args:
            get_proposal_object_input (GetProposalObjectInput): Input containing user_email, project_name, and proposal_title.

        Returns:
            None: If the proposal object is set successfully.
        """

        proposal: Proposal = self.get_proposal_by_title(
            project=project, title=proposal_title
        )

        proposal.extracted_object = proposal_object

    async def set_proposal_str_to_project(
        self,
        project: Project,
        proposal_str: str,
        proposal_title: str,
    ) -> None:
        """Set the proposal string for a project.

        Args:
            project (Project): The project to which the proposal belongs.
            proposal_str (str): The string representation of the proposal.
            proposal_title (str): The title of the proposal.

        Returns:
            None: If the proposal string is set successfully.
        """

        proposal: Proposal = self.get_proposal_by_title(
            project=project, title=proposal_title
        )

        proposal.proposal_str = proposal_str

    async def get_proposal_object_by_title(
        self, project: Project, proposal_title: str
    ) -> ProposalWithPolygonAndValidation:
        """Get the proposal object by title.
        Args:
            user (User): The user requesting the proposal object.
            project (Project): The project to which the proposal belongs.
            proposal_title (str): The title of the proposal.
        Returns:
            ProposalWithPolygonAndValidation: The structured proposal object if found, otherwise raises an error.
        """

        proposal: Proposal = self.get_proposal_by_title(
            project=project, title=proposal_title
        )

        if not proposal.extracted_object:
            logger.error(
                "USER HANDLER => Proposal %s has not been extracted.",
                proposal_title,
            )

            raise ProposalNotExtracted(proposal_title=proposal.title)

        return proposal.extracted_object

    async def set_proposal_validation_by_title(
        self,
        project: Project,
        proposal_title: str,
        validation_report: ValidationReport,
    ) -> None:
        """Set the validation report for a proposal object in a project.

        Args:
            user (User): The user who owns the project.
            project (Project): The project to which the proposal belongs.
            proposal_title (str): The title of the proposal.
            validation_report (ValidationReport): The validation report to set.

        Returns:
            None: If the validation report is set successfully.
        """

        proposal: Proposal = self.get_proposal_by_title(
            project=project, title=proposal_title
        )

        proposal.validation_object = validation_report

    async def create_proposal_object(
        self, create_proposal_object_input: CreateProposalObjectInput
    ) -> ProposalWithPolygonAndValidation:
        """Create and return a structured proposal object from the proposal bytes.

        Args:
            proposal_bytes (bytes): The raw bytes of the proposal.
            packs (List[str]): The list of packs associated with the proposal.

        Returns:
            Optional[ProposalWithPolygonAndValidation]: The structured proposal object if successfully created, otherwise None.
        """

        user: User = await self.get_user(
            get_user_input=GetUserInput(
                user_email=create_proposal_object_input.user_email
            )
        )

        project: Project = self.get_project_by_name(
            user=user, project_name=create_proposal_object_input.project_name
        )

        if not project.packs:
            logger.error(
                "USER HANDLER => No packs found in project %s.",
                create_proposal_object_input.project_name,
            )

            raise NoPacksInProject(project_name=project.name)

        proposal_file: ProposalFile = await self.get_proposal_file_by_title(
            project=project, proposal_title=create_proposal_object_input.proposal_title
        )

        (
            proposal_object,
            validation_report,
            proposal_str,
        ) = await ProposalHandler().get_proposal_object(
            proposal_bytes=proposal_file.pdf_content, packs=project.packs
        )

        await self.set_proposal_object_to_project(
            project=project,
            proposal_object=proposal_object,
            proposal_title=create_proposal_object_input.proposal_title,
        )

        await self.set_proposal_validation_by_title(
            project=project,
            proposal_title=create_proposal_object_input.proposal_title,
            validation_report=validation_report,
        )

        await self.set_proposal_str_to_project(
            project=project,
            proposal_str=proposal_str,
            proposal_title=create_proposal_object_input.proposal_title,
        )

        await user.save()

        return proposal_object

    async def create_proposal_object_validation(
        self, create_proposal_object_input: CreateProposalObjectValidationInput
    ) -> ValidationReport:
        """Create a proposal object and validate it.
        Args:
            create_proposal_object_input (CreateProposalObjectValidationInput): Input containing user_email, project_name, and proposal_title.
        """

        user: User = await self.get_user(
            get_user_input=GetUserInput(
                user_email=create_proposal_object_input.user_email
            )
        )

        project: Project = self.get_project_by_name(
            user=user, project_name=create_proposal_object_input.project_name
        )

        if not project.packs:
            logger.error(
                "USER HANDLER => No packs found in project %s.",
                create_proposal_object_input.project_name,
            )

            raise NoPacksInProject(project_name=project.name)

        proposal_object: ProposalWithPolygonAndValidation = (
            await self.get_proposal_object_by_title(
                project=project,
                proposal_title=create_proposal_object_input.proposal_title,
            )
        )

        proposal_object, proposal_validation = ProposalObjectHandler(
            proposal_object=proposal_object
        ).validate_proposal_object()

        await self.set_proposal_validation_by_title(
            project=project,
            proposal_title=create_proposal_object_input.proposal_title,
            validation_report=proposal_validation,
        )

        await self.set_proposal_object_to_project(
            project=project,
            proposal_object=proposal_object,
            proposal_title=create_proposal_object_input.proposal_title,
        )

        await user.save()

        return proposal_validation

    async def get_proposal_validation_by_title(
        self, get_proposal_validation_input: GetProposalObjectValidationInput
    ) -> ValidationReport:
        """Get the validation report for a proposal object by title.

        Args:
            user (User): The user who owns the project.
            project (Project): The project to which the proposal belongs.
            proposal_title (str): The title of the proposal.

        Returns:
            ValidationReport: The validation report for the proposal object.

        """

        user: User = await self.get_user(
            get_user_input=GetUserInput(
                user_email=get_proposal_validation_input.user_email
            )
        )

        project: Project = self.get_project_by_name(
            user=user, project_name=get_proposal_validation_input.project_name
        )

        proposal: Proposal = self.get_proposal_by_title(
            project=project, title=get_proposal_validation_input.proposal_title
        )

        if not proposal.validation_object:
            logger.error(
                "USER HANDLER => Validation report for proposal %s not found.",
                proposal.title,
            )

            raise ProposalValidationNotCreated(proposal_title=proposal.title)

        return proposal.validation_object
