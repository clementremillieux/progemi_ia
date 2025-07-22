"""API exception module for handling API errors."""

from fastapi import HTTPException, status


class UserAlreadyExists(HTTPException):
    """Exception raised when a user already exists."""

    status_code = status.HTTP_409_CONFLICT

    detail = "User already exists"

    def __init__(self) -> None:
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserNotExists(HTTPException):
    """Exception raised when a user does not exist."""

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "User {user_id} does not exist"

    def __init__(self, user_id: str) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.detail.format(user_id=user_id),
        )


class FileNameMissing(HTTPException):
    """Exception raised when a file name is missing."""

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "File name is missing"

    def __init__(self) -> None:
        super().__init__(status_code=self.status_code, detail=self.detail)


class ProjectNotFound(HTTPException):
    """Exception raised when a project is not found."""

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "Project {project_name} does not exist"

    def __init__(self, project_name: str) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.detail.format(project_name=project_name),
        )


class ProposalNotFound(HTTPException):
    """Exception raised when a proposal is not found."""

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "Proposal {proposal_id} does not exist"

    def __init__(self, proposal_id: str) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.detail.format(proposal_id=proposal_id),
        )


class ProposalNotExtracted(HTTPException):
    """Exception raised when a proposal is not extracted."""

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "Proposal {proposal_title} has not been extracted"

    def __init__(self, proposal_title: str) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.detail.format(proposal_title=proposal_title),
        )


class NoPacksInProject(HTTPException):
    """Exception raised when no packs are found in a project."""

    status_code = status.HTTP_404_NOT_FOUND

    detail = "No packs found in project {project_name}"

    def __init__(self, project_name: str) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.detail.format(project_name=project_name),
        )


class ProposalObjectNotCreated(HTTPException):
    """Exception raised when a proposal object is not created."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    detail = "Proposal object for {proposal_title} has not been created"

    def __init__(self, proposal_title: str) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.detail.format(proposal_title=proposal_title),
        )


class ProposalValidationNotCreated(HTTPException):
    """Exception raised when a proposal validation is not created."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    detail = "Proposal validation for {proposal_title} has not been created"

    def __init__(self, proposal_title: str) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.detail.format(proposal_title=proposal_title),
        )


class PacksNameNotExists(HTTPException):
    """Exception raised when a pack name does not exist."""

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "Pack name '{pack_name}' does not exist"

    def __init__(self, pack_name: str) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.detail.format(pack_name=pack_name),
        )
