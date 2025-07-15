"""Proposal object exceptions."""

from fastapi import HTTPException, status


class AzureDocumentIntelligenceError(HTTPException):
    """Exception raised when there is an error with Azure Document Intelligence."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    detail = "Error with Azure Document Intelligence"

    def __init__(self) -> None:
        super().__init__(status_code=self.status_code, detail=self.detail)


class ProposalObjectNotCreated(HTTPException):
    """Exception raised when a proposal object is not created."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    detail = "Proposal object has not been created"

    def __init__(self) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
        )
