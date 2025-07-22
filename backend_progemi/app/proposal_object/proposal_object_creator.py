"""Proposal Object Creator Module."""

import base64
from typing import List, Optional, Tuple, Type

from azure.ai.documentintelligence.models import (
    AnalyzeResult,
)

from app.cost.cost import CostTracker

from app.ocr.azure_di_handler import AzureDIHandler

from app.proposal_object.proposal_section_analysis import (
    ProposalSectionAnalysis,
    StructureProduitsDevis,
)

from app.proposal_object.schemas import Devis, ProposalWithPolygonAndValidation

from app.proposal_object.exceptions import ProposalObjectNotCreated

from app.proposal_object.proposal_polygone import ProposalPolygonHandler

from app.proposal_object.proposal_text_analysis import ProposalTextAnalyzer

from config.logger_config import logger


class ProposalObjectCreator:
    """Class to create a proposal object (Devis)."""

    def __init__(self, proposal_bytes: bytes, cost_tracker: CostTracker) -> None:
        """Initialize the ProposalObjectCreator with a proposal object."""

        self.azure_di_handler = AzureDIHandler()

        self.cost_tracker: CostTracker = cost_tracker

        self.proposal_bytes: bytes = proposal_bytes

    async def create(
        self, devis_model: Type[Devis]
    ) -> Tuple[ProposalWithPolygonAndValidation, str, AnalyzeResult]:
        """Create and return the proposal object."""

        proposal_str, analyze_result = self.azure_di_handler.analyze_and_extract(
            file_binary=self.proposal_bytes
        )

        file_base64: str = base64.b64encode(self.proposal_bytes).decode("utf-8")

        proposal_sections: Optional[
            StructureProduitsDevis
        ] = await ProposalSectionAnalysis(
            cost_tracker=self.cost_tracker,
            proposal_str=proposal_str,
            file_base64=file_base64,
        ).get_sections()

        if not proposal_sections:
            logger.error(
                "PROPOSAL OBJECT CREATOR => Failed to create proposal object: No sections found in the proposal."
            )

            raise ProposalObjectNotCreated()

        proposal_object: Optional[Devis] = await ProposalTextAnalyzer(
            cost_tracker=self.cost_tracker, file_base64=file_base64
        ).analyze_and_structure(
            raw_proposal=proposal_str,
            section_analysis=proposal_sections.model_dump_json(indent=2),
            devis_model=devis_model,
        )

        if not proposal_object:
            logger.error(
                "PROPOSAL OBJECT CREATOR => Failed to create proposal object: No structured proposal found."
            )

            raise ProposalObjectNotCreated()

        proposal_with_polygon: ProposalWithPolygonAndValidation = (
            ProposalPolygonHandler(
                proposal_object=proposal_object,
                analyze_result=analyze_result,
            ).add_polygon_to_products()
        )

        return proposal_with_polygon, proposal_str, analyze_result
