"""API exception module for handling API errors."""

from fastapi import HTTPException, status


class InvalidToken(HTTPException):
    """Exception raised when an invalid token is provided."""

    status_code = status.HTTP_401_UNAUTHORIZED

    detail = "Invalid token"

    def __init__(self) -> None:
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserTokenError(HTTPException):
    """Exception raised when a user token level error occurs."""

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "User token not found :{reason}"

    def __init__(self, reason: str) -> None:
        """Initialize the exception with a reason."""

        self.detail = self.detail.format(reason=reason)

        super().__init__(status_code=self.status_code, detail=self.detail)


class PacksError(HTTPException):
    """Exception raised when there is an error with packs."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    detail = "Packs error : {reason}"

    def __init__(self, reason: str) -> None:
        self.detail = self.detail.format(reason=reason)

        super().__init__(status_code=self.status_code, detail=self.detail)


class ProjectError(HTTPException):
    """Exception raised when there is an error with a project."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    detail = "Project error : {reason}"

    def __init__(self, reason: str) -> None:
        self.detail = self.detail.format(reason=reason)

        super().__init__(status_code=self.status_code, detail=self.detail)
