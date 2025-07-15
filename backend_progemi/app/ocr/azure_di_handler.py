"""Azure Document Intelligence handler for processing documents."""

from typing import List, Optional, Tuple

from app.ocr.exceptions import (
    AzureDocumentIntelligenceAnalyzeError,
    AzureDocumentIntelligenceParsingError,
)

from app.ocr.utils import build_document_text

from azure.core.credentials import AzureKeyCredential

from azure.ai.documentintelligence.models import (
    DocumentAnalysisFeature,
    AnalyzeResult,
    DocumentContentFormat,
    DocumentParagraph,
    DocumentTable,
    DocumentStyle,
    DocumentPage,
)

from azure.ai.documentintelligence import DocumentIntelligenceClient

from config.config import env_param

from config.logger_config import logger


class AzureDIHandler:
    """Handler for Azure Document Intelligence operations."""

    def __init__(self):
        """Initialize the Azure Document Intelligence client."""

        self.document_intelligence_client = DocumentIntelligenceClient(
            endpoint=env_param.AZURE_DI_URL,
            credential=AzureKeyCredential(env_param.AZURE_DI_KEY),
        )

        self.features = [
            DocumentAnalysisFeature.STYLE_FONT,
            DocumentAnalysisFeature.OCR_HIGH_RESOLUTION,
        ]

    def analyze_document(self, file_binary: bytes) -> AnalyzeResult:
        """Analyze the document using Azure Document Intelligence."""

        poller = self.document_intelligence_client.begin_analyze_document(
            model_id="prebuilt-layout",
            body=file_binary,
            features=self.features,
            output_content_format=DocumentContentFormat.MARKDOWN,
        )

        analyze_result: AnalyzeResult = poller.result()

        return analyze_result

    def process_results(self, analyze_result: AnalyzeResult) -> Optional[str]:
        """Process the analysis results and extract relevant information."""

        pages: Optional[List[DocumentPage]] = analyze_result.pages

        paragraphs: Optional[List[DocumentParagraph]] = analyze_result.paragraphs

        tables: Optional[List[DocumentTable]] = analyze_result.tables

        styles: Optional[List[DocumentStyle]] = analyze_result.styles

        if not pages or not paragraphs or not tables or not styles:
            logger.warning(
                "Azure Document Intelligence did not return all expected results. "
                "Pages, paragraphs, tables, or styles are missing."
            )

            return None

        document_str = build_document_text(
            pages=pages,
            paragraphs=paragraphs,
            tables=tables,
            styles=styles,
        )

        return document_str

    def analyze_and_extract(self, file_binary: bytes) -> Tuple[str, AnalyzeResult]:
        """Analyze the document and extract structured information."""

        analyze_result = self.analyze_document(file_binary=file_binary)

        if not analyze_result:
            logger.error("Failed to analyze document with Azure Document Intelligence.")

            raise AzureDocumentIntelligenceAnalyzeError()

        document_str = self.process_results(analyze_result=analyze_result)

        if not document_str:
            logger.error("Failed to process results from Azure Document Intelligence.")

            raise AzureDocumentIntelligenceParsingError()

        return document_str, analyze_result
