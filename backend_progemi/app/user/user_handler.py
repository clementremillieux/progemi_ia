"""User handler module"""

from typing import List, Optional

from fastapi import UploadFile

from pymongo.errors import DuplicateKeyError

from beanie.odm.fields import PydanticObjectId

from app.user.exception import (
    FileNameMissing,
    NoPacksInProject,
    PacksNameNotExists,
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
)

from app.auth.schemas import ConnectedUser

from app.progemi_api.schemas import PackProgemi, ProjectProgemi

from app.proposal_object.proposal_validate_results import (
    ValidationReport,
)

from app.proposal_object.proposal_handler import ProposalHandler

from app.progemi_api.progemi_api_handler import ProgemiAPIHandler

from app.proposal_object.schemas import ProposalWithPolygonAndValidation

from app.proposal_object.proposal_object_analyzer import ProposalObjectHandler

from config.logger_config import logger


class UserHandler:
    """User handler class to manage user-related operations."""

    def __init__(self):
        """Initialize the UserHandler"""

    def get_packs_names_from_progemi_packs(self, packs: List[PackProgemi]) -> List[str]:
        """Get pack names from Progemi packs.

        Args:
            packs (List[PackProgemi]): The list of Progemi packs.

        Returns:
            List[str]: A list of pack names.
        """

        return [pack.libellelot for pack in packs]

    def build_new_user(self, new_user_params: NewUserInput) -> User:
        """Build a new user object.

        Args:
            user_name (str): The name of the user.
            user_id (str): The ID of the user.

        Returns:
            User: A User object with default values.
        """

        return User(
            name=new_user_params.user_name,
            user_id=new_user_params.user_id,
            projects=[],
            user_packs=new_user_params.user_packs,
        )

    async def create_user(self, new_user_params: NewUserInput) -> None:
        """Create a new user.

        Args:
            user_name (str): The name of the user.
            user_id (str): The ID of the user.

        Returns:
            User: A User object with default values.

        Raises:
            UserAlreadyExists: If the user already exists.
            DuplicateKeyError: If there is a duplicate key error during insertion.
        """

        try:
            new_user: User = self.build_new_user(new_user_params=new_user_params)

            await new_user.insert()

        except DuplicateKeyError as e:
            logger.error("USER HANDLER => User %s already exists.", new_user.user_id)

            raise UserAlreadyExists() from e

    async def get_user(self, connected_user: ConnectedUser) -> User:
        """Get user by user_id.

        Args:
            connected_user (ConnectedUser): The connected user object.
        Returns:
            User: The user object if found.
        Raises:
            UserNotExists: If the user does not exist.
        """

        user: Optional[User] = await User.find_one(
            User.user_id == connected_user.user_id
        )

        if not user:
            logger.error("USER HANDLER => User %s not found.", connected_user.user_id)

            raise UserNotExists(user_id=connected_user.user_id)

        logger.debug(
            "USER HANDLER => User %s retrieved successfully.", connected_user.user_id
        )

        return user

    async def get_user_packs_names(self, connected_user: ConnectedUser) -> List[str]:
        """Get all pack names associated with a user.

        Args:
            get_user_input (GetUserInput): Input containing user_id to retrieve the user packs.
        Returns:
            List[str]: A list of pack names associated with the user.
        Raises:
            UserNotExists: If the user does not exist.
        """

        user: User = await self.get_user(connected_user=connected_user)

        return [pack.libellelot for pack in user.user_packs]

    async def delete_user(self, connected_user: ConnectedUser) -> None:
        """Delete user by user_id.

        Args:
            connected_user (ConnectedUser): The connected user object.
        Returns:
            None: If the user is deleted successfully.
        Raises:
            UserNotExists: If the user does not exist.
        """

        user: User = await self.get_user(connected_user=connected_user)

        await user.delete()

        logger.debug(
            "USER HANDLER => User %s deleted successfully.",
            connected_user.user_id,
        )

    async def get_all_user_ids(self) -> List[str]:
        """Get all user IDs.

        Returns:
            List[str]: A list of all user IDs.
        """

        users: List[User] = await User.find_all().to_list()

        user_ids: List[str] = [str(user.id) for user in users]

        logger.debug("USER HANDLER => Retrieved %d user IDs.", len(user_ids))

        return user_ids

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
            title=file.filename,
            status=ProposalStatus.PENDING,
            pdf_id=proposal_file.id,
            packs=[],
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

    async def create_new_project(
        self, new_project_input: NewProjectInput, connected_user: ConnectedUser
    ) -> None:
        """Create a new project for a user.

        Args:
            user (User): The user object to which the project will be added.
            project_name (str): The name of the new project.

        Returns:
            None: If the project is created successfully.

        Raises:
            DuplicateKeyError: If a project with the same name already exists for the user.
        """

        user: User = await self.get_user(connected_user=connected_user)

        if any(proj.name == new_project_input.project_name for proj in user.projects):
            logger.error(
                "USER HANDLER => Project %s already exists for user %s.",
                new_project_input.project_name,
                user.user_id,
            )

            raise DuplicateKeyError(
                f"Project {new_project_input.project_name} already exists."
            )

        new_project = Project(
            name=new_project_input.project_name,
            proposals=[],
            project_packs=[],
            is_pack_to_choose=True,
        )

        user.projects.append(new_project)

        await user.save()

        logger.debug(
            "USER HANDLER => Project %s created successfully for user %s.",
            new_project_input.project_name,
            user.user_id,
        )

    async def get_progemi_user_project_names(
        self, connected_user: ConnectedUser
    ) -> List[str]:
        """Get all project names for a connected user.

        Args:
            connected_user (ConnectedUser): The connected user object.

        Returns:
            List[str]: A list of project names for the user.
        """

        projects_progemi: List[
            ProjectProgemi
        ] = await ProgemiAPIHandler().get_user_project(connected_user=connected_user)

        projects_progemi_names: List[str] = [
            project.designationprojet for project in projects_progemi
        ]

        logger.debug(
            "USER HANDLER => Retrieved %d  PROGEMI projects for user %s.",
            len(projects_progemi_names),
            connected_user.user_id,
        )

        return projects_progemi_names

    def get_new_progemi_project_names(
        self, progemi_user_project_names: List[str], ia_db_projects_name: List[str]
    ) -> List[str]:
        """Get progemi project names that are not in the IA database."""

        not_in_ia_db_projects: List[str] = []

        for project_name in progemi_user_project_names:
            if project_name not in ia_db_projects_name:
                logger.debug(
                    "USER HANDLER => New Progemi project found: %s.", project_name
                )
                not_in_ia_db_projects.append(project_name)

        logger.debug(
            "USER HANDLER => Found %d new Progemi projects not in IA DB.",
            len(not_in_ia_db_projects),
        )

        return not_in_ia_db_projects

    def get_progemi_project_to_delete(
        self, progemi_user_project_names: List[str], ia_db_projects_name: List[str]
    ) -> List[str]:
        """Get Progemi project names that are not in the PROGEMI database anymore."""

        not_in_progemi_db_projects: List[str] = []

        for project_name in ia_db_projects_name:
            if project_name not in progemi_user_project_names:
                logger.debug(
                    "USER HANDLER => Project AI not found in PROGEMI DB: %s.",
                    project_name,
                )
                not_in_progemi_db_projects.append(project_name)

        logger.debug(
            "USER HANDLER => Found %d Progemi projects not in PROGEMI DB to remove.",
            len(not_in_progemi_db_projects),
        )

        return not_in_progemi_db_projects

    async def create_new_project_from_progemi(
        self, new_project_name: str, connected_user: ConnectedUser
    ) -> None:
        """Create a new project from Progemi for a connected user."""

        logger.debug(
            "USER HANDLER => Creating new project %s from Progemi for user %s.",
            new_project_name,
            connected_user.user_id,
        )

        packs = await ProgemiAPIHandler().get_user_packs(token=connected_user.token)

        new_project_input = NewProjectInput(
            user_id=connected_user.user_id,
            project_name=new_project_name,
            packs=[p.libellelot for p in packs],
        )

        await self.create_new_project(
            new_project_input=new_project_input, connected_user=connected_user
        )

    async def run_delta_projects(self, connected_user: ConnectedUser) -> None:
        """Run delta projects for all users."""

        progemi_user_project_names: List[
            str
        ] = await self.get_progemi_user_project_names(connected_user=connected_user)

        ia_db_projects: List[str] = await self.get_all_projects_name(
            connected_user=connected_user
        )

        new_projects: List[str] = self.get_new_progemi_project_names(
            progemi_user_project_names=progemi_user_project_names,
            ia_db_projects_name=ia_db_projects,
        )

        for project_name in new_projects:
            await self.create_new_project_from_progemi(
                new_project_name=project_name, connected_user=connected_user
            )

        ia_db_projects = await self.get_all_projects_name(connected_user=connected_user)

        projects_to_delete: List[str] = self.get_progemi_project_to_delete(
            progemi_user_project_names=progemi_user_project_names,
            ia_db_projects_name=ia_db_projects,
        )

        for project_name in projects_to_delete:
            delete_project_input = DeleteProjectInput(
                user_id=connected_user.user_id, project_name=project_name
            )
            await self.delete_project(
                delete_project_input=delete_project_input, connected_user=connected_user
            )

    async def delete_project(
        self, delete_project_input: DeleteProjectInput, connected_user: ConnectedUser
    ) -> None:
        """Delete a project from a user's projects.

        Args:
            delete_project_input (DeleteProjectInput): Input containing user_id and project_name.

        Returns:
            None: If the project is deleted successfully.

        Raises:
            ProjectNotFound: If the project is not found for the user.
            UserNotExists: If the user does not exist.
        """

        user: User = await self.get_user(connected_user=connected_user)

        project: Project = self.get_project_by_name(
            user=user, project_name=delete_project_input.project_name
        )

        user.projects.remove(project)

        await user.save()

        logger.debug(
            "USER HANDLER => Project %s deleted successfully for user %s.",
            delete_project_input.project_name,
            user.user_id,
        )

    async def get_all_user_projects(
        self, connected_user: ConnectedUser
    ) -> List[Project]:
        """Get all projects for a connected user.

        Args:
            connected_user (ConnectedUser): The connected user object.

        Returns:
            List[Project]: A list of projects associated with the user.
        """

        user: User = await self.get_user(connected_user=connected_user)

        if not user.projects:
            logger.warning(
                "USER HANDLER => No projects found for user %s.", user.user_id
            )

        return user.projects

    async def get_all_projects_name(self, connected_user: ConnectedUser) -> List[str]:
        """Get the names of all projects for a user."""

        user: User = await self.get_user(connected_user=connected_user)

        if not user.projects:
            logger.warning(
                "USER HANDLER => No projects found for user %s.", user.user_id
            )

            return []

        project_names: List[str] = [project.name for project in user.projects]

        logger.debug(
            "USER HANDLER => Retrieved projects names for user %s: %s.",
            user.user_id,
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
                user.user_id,
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
        self,
        upload_proposal_input: UploadProposalInput,
        file: UploadFile,
        connected_user: ConnectedUser,
    ) -> None:
        """Upload a proposal for a user to a project.

        Args:
            upload_proposal_input (UploadProposalInput): Input containing user_id and project_name.
            file (UploadFile): The file to be uploaded as a proposal.

        Returns:
            None: If the proposal is uploaded successfully.

        Raises:
            FileNameMissing: If the file name is missing.
            ProjectNotFound: If the project is not found for the user.
        """

        proposal: Proposal = await self.insert_proposal_file(file=file)

        user: User = await self.get_user(connected_user=connected_user)

        project: Project = self.get_project_by_name(
            user=user, project_name=upload_proposal_input.project_name
        )

        project.proposals.append(proposal)

        await user.save()

        logger.debug(
            "USER HANDLER => Proposal %s uploaded for user %s in project %s.",
            file.filename,
            connected_user.user_id,
            upload_proposal_input.project_name,
        )

    async def delete_proposal_by_title(
        self, delete_proposal_input: DeleteProposalInput, connected_user: ConnectedUser
    ) -> None:
        """Delete a proposal from a user's project and the database.

        Args:
            delete_proposal_input (DeleteProposalInput): Input containing user_id, project_name, and proposal_id.

        Returns:
            None: If the proposal is deleted successfully.

        Raises:
            ProjectNotFound: If the project is not found for the user.
            UserNotExists: If the user does not exist.
        """

        user: User = await self.get_user(connected_user=connected_user)

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
            connected_user.user_id,
            delete_proposal_input.project_name,
        )

    async def get_proposal_by_id(
        self, get_proposal_input: GetProposalInput
    ) -> ProposalFile:
        """Get a proposal file by its ID.

        Args:
            get_proposal_input (GetProposalInput): Input containing user_id and proposal_id.

        Returns:
            ProposalFile: The proposal file object if found.

        """

        proposal_file: ProposalFile = await self.get_proposal_file_by_id(
            proposal_id=get_proposal_input.proposal_id
        )

        return proposal_file

    async def get_all_user_project_proposal_infos(
        self,
        get_all_proposals_input: GetAllProposalsInput,
        connected_user: ConnectedUser,
    ) -> List[ProposalInfos]:
        """Get all proposals for a user's projects.

        Args:
            get_all_proposals_input (GetAllProposalsInput): Input containing user_id and project_name.

        Returns:
            list[Proposal]: A list of proposals for the user's projects.
        """

        user: User = await self.get_user(connected_user=connected_user)

        project = self.get_project_by_name(
            user=user, project_name=get_all_proposals_input.project_name
        )

        return [
            ProposalInfos(
                **proposal.model_dump(exclude="packs"),
                packs=self.get_all_proposal_packs(proposal_object=proposal),
            )
            for proposal in project.proposals
        ]

    @staticmethod
    def get_all_proposal_packs(proposal_object: Proposal) -> List[str]:
        """
        Get the list of packs associated with a proposal object.

        Args:
            proposal_object (Proposal): The proposal object.
        """

        all_packs: List[str] = []

        if not proposal_object.extracted_object:
            return []

        for produit in proposal_object.extracted_object.devis_produits:
            if produit.lot:
                all_packs.append(produit.lot)

        return list(set(all_packs))

    async def get_all_user_project_proposal_files(
        self,
        get_all_proposals_input: GetAllProposalsInput,
        connected_user: ConnectedUser,
    ) -> List[ProposalFile]:
        """Get all proposal files for a user's projects.

        Args:
            get_all_proposals_input (GetAllProposalsInput): Input containing user_id and project_name.

        Returns:
            list[ProposalFile]: A list of proposal files for the user's projects.
        """

        user: User = await self.get_user(connected_user=connected_user)

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
        self,
        get_project_packs_input: GetProjectPacksInput,
        connected_user: ConnectedUser,
    ) -> List[PackProgemi]:
        """Get all packs associated with a project for a user.

        Args:
            get_project_packs_input (GetProjectPacksInput): Input containing user_id and project_name.

        Returns:
            List[str]: A list of pack names associated with the project.

        Raises:
            UserNotExists: If the user does not exist.
            ProjectNotFound: If the project is not found for the user.
        """

        user: User = await self.get_user(connected_user=connected_user)

        project: Project = self.get_project_by_name(
            user=user, project_name=get_project_packs_input.project_name
        )

        return project.project_packs

    async def update_project_packs(
        self,
        update_project_packs_input: UpdateProjectPacksInput,
        connected_user: ConnectedUser,
    ) -> None:
        """Update the packs associated with a project for a user.

        Args:
            update_project_packs_input (UpdateProjectPacksInput): Input containing user_id, project_name, and packs.
        """

        user: User = await self.get_user(connected_user=connected_user)

        project: Project = self.get_project_by_name(
            user=user, project_name=update_project_packs_input.project_name
        )

        packs_to_add: List[PackProgemi] = []

        for pack_name in update_project_packs_input.packs_name:
            pack_to_add = next(
                (pack for pack in user.user_packs if pack.libellelot == pack_name),
                None,
            )

            if not pack_to_add:
                raise PacksNameNotExists(
                    pack_name=pack_name,
                )

            packs_to_add.append(pack_to_add)

        project.project_packs = packs_to_add

        project.is_pack_to_choose = False

        await user.save()

        logger.debug(
            "USER HANDLER => Packs updated for project %s of user %s.",
            update_project_packs_input.project_name,
            connected_user.user_id,
        )

    async def get_proposal_extracted_object(
        self,
        get_proposal_extracted_object_input: GetProposalExtractedObjectInput,
        connected_user: ConnectedUser,
    ) -> ProposalWithPolygonAndValidation:
        """Get the extracted object from a proposal.

        Args:
            get_proposal_extracted_object_input (GetProposalExtractedObjectInput): Input containing user_id, project_name, and title.

        Returns:
            ProposalWithPolygonAndValidation: The extracted object from the proposal.
        """

        user: User = await self.get_user(connected_user=connected_user)

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
        self,
        set_proposal_extracted_object_input: SetProposalExtractedObjectInput,
        connected_user: ConnectedUser,
    ) -> ProposalWithPolygonAndValidation:
        """Set the extracted object for a proposal.

        Args:
            set_proposal_extracted_object_input (SetProposalExtractedObjectInput): Input containing user_id, project_name, title, and extracted_object.
        Returns:
            None: If the extracted object is set successfully.
        """

        logger.debug(
            "USER HANDLER => Setting extracted object for proposal %s in project %s of user %s.",
            set_proposal_extracted_object_input.title,
            set_proposal_extracted_object_input.project_name,
            connected_user.user_id,
        )

        user: User = await self.get_user(connected_user=connected_user)

        logger.debug(
            "USER HANDLER => User %s retrieved successfully.",
            user.user_id,
        )

        project: Project = self.get_project_by_name(
            user=user, project_name=set_proposal_extracted_object_input.project_name
        )

        logger.debug(
            "USER HANDLER => Project %s retrieved successfully for user %s.",
            project.name,
            user.user_id,
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
            connected_user.user_id,
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
            get_proposal_object_input (GetProposalObjectInput): Input containing user_id, project_name, and proposal_title.

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

    async def set_proposal_packs_by_title(
        self,
        project: Project,
        proposal_title: str,
        proposal_object: ProposalWithPolygonAndValidation,
    ) -> None:
        """Set the packs associated with a proposal object in a project.

        Args:
            project (Project): The project to which the proposal belongs.
            proposal_title (str): The title of the proposal.
            proposal_object (ProposalWithPolygonAndValidation): The proposal object containing the packs.

        Returns:
            None: If the packs are set successfully.
        """

        proposal: Proposal = self.get_proposal_by_title(
            project=project, title=proposal_title
        )

        proposal.packs = proposal_object.packs

    async def create_proposal_object(
        self,
        create_proposal_object_input: CreateProposalObjectInput,
        connected_user: ConnectedUser,
    ) -> ProposalWithPolygonAndValidation:
        """Create and return a structured proposal object from the proposal bytes.

        Args:
            proposal_bytes (bytes): The raw bytes of the proposal.
            packs (List[str]): The list of packs associated with the proposal.

        Returns:
            Optional[ProposalWithPolygonAndValidation]: The structured proposal object if successfully created, otherwise None.
        """

        user: User = await self.get_user(connected_user=connected_user)

        project: Project = self.get_project_by_name(
            user=user, project_name=create_proposal_object_input.project_name
        )

        if not project.project_packs:
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
            proposal_bytes=proposal_file.pdf_content,
            packs=self.get_packs_names_from_progemi_packs(project.project_packs),
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
        self,
        create_proposal_object_input: CreateProposalObjectValidationInput,
        connected_user: ConnectedUser,
    ) -> ValidationReport:
        """Create a proposal object and validate it.
        Args:
            create_proposal_object_input (CreateProposalObjectValidationInput): Input containing user_id, project_name, and proposal_title.
        """

        user: User = await self.get_user(connected_user=connected_user)

        project: Project = self.get_project_by_name(
            user=user, project_name=create_proposal_object_input.project_name
        )

        if not project.project_packs:
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
        self,
        get_proposal_validation_input: GetProposalObjectValidationInput,
        connected_user: ConnectedUser,
    ) -> ValidationReport:
        """Get the validation report for a proposal object by title.

        Args:
            user (User): The user who owns the project.
            project (Project): The project to which the proposal belongs.
            proposal_title (str): The title of the proposal.

        Returns:
            ValidationReport: The validation report for the proposal object.

        """

        user: User = await self.get_user(connected_user=connected_user)

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
