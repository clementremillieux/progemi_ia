"""Azure Document Intelligence error handling module."""

from fastapi import HTTPException, status


class AzureDocumentIntelligenceAnalyzeError(HTTPException):
    """Exception raised when there is an error with Azure Document Intelligence."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    detail = "Error with Azure Document Intelligence API during analysis"

    def __init__(self) -> None:
        super().__init__(status_code=self.status_code, detail=self.detail)


class AzureDocumentIntelligenceParsingError(HTTPException):
    """Exception raised when there is an error with Azure Document Intelligence."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    detail = "Error with Azure Document Intelligence API during parsing"

    def __init__(self) -> None:
        super().__init__(status_code=self.status_code, detail=self.detail)
