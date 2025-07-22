"""Proposal Handler Module."""

import re

import unicodedata

from enum import Enum

from typing import List, Tuple, Type

from azure.ai.documentintelligence.models import (
    AnalyzeResult,
)

from app.cost import cost
from app.cost.cost import CostTracker

from app.proposal_object.proposal_retry import ProposalRetry

from app.proposal_object.proposal_polygone import ProposalPolygonHandler

from app.proposal_object.proposal_validate_results import ValidationReport

from app.proposal_object.proposal_object_creator import ProposalObjectCreator

from app.proposal_object.proposal_object_analyzer import ProposalObjectHandler

from app.proposal_object.schemas import Devis, Produit, ProposalWithPolygonAndValidation

from config.logger_config import logger


class ProposalHandler:
    """Class to handle proposal-related operations."""

    def make_identifier(self, s: str) -> str:
        """Convert a string to a valid identifier by removing accents and special characters."""

        s_norm = unicodedata.normalize("NFKD", s)

        s_ascii = "".join(ch for ch in s_norm if unicodedata.category(ch) != "Mn")

        tmp = re.sub(r"\W+", "_", s_ascii)

        if re.match(r"^\d", tmp):
            tmp = "_" + tmp

        return tmp.upper().strip("_")

    def _build_lot_enum(self, packs: List[str]) -> Enum:
        """
        Build an Enum for the packs in a proposal.
        """

        members = {}

        for pack in packs:
            key = self.make_identifier(pack)

            if key in members:
                continue

            members[key] = pack

        return Enum("Lot", members)

    def inject_lot_enum(
        self,
        packs: List[str],
        produit_model: Type[Produit],
        devis_model: Type[Devis],
    ) -> Type[Devis]:
        """
        Inject an Enum for the packs into the Produit model and update the Devis model schema.
        """

        Lot = self._build_lot_enum(packs)

        produit_model.__annotations__["lot"] = Lot

        produit_model.model_fields["lot"].annotation = Lot

        produit_model.model_rebuild(force=True)

        devis_model.model_rebuild(force=True)

        logger.info(
            "PROPOSAL HANDLER => devis_model schema updated with packs: %s",
            devis_model.model_json_schema(),
        )
        return devis_model

    async def get_proposal_object(
        self, proposal_bytes: bytes, packs: List[str]
    ) -> Tuple[ProposalWithPolygonAndValidation, ValidationReport, str]:
        """
        Create and return a structured proposal object from the proposal bytes.
        """

        cost_tracker = CostTracker()

        devis_model = self.inject_lot_enum(
            packs=packs,
            produit_model=Produit,
            devis_model=Devis,
        )

        proposal_object_creator = ProposalObjectCreator(
            proposal_bytes=proposal_bytes,
            cost_tracker=cost_tracker,
        )

        (
            proposal_object,
            proposal_str,
            analyze_result,
        ) = await proposal_object_creator.create(devis_model=devis_model)

        # logger.info(
        #     "PROPOSAL HANDLER => Proposal object: %s",
        #     proposal_object.model_dump_json(indent=2),
        # )

        proposal_object, report = await self.validate_proposal_object(
            proposal_object=proposal_object
        )

        logger.info(
            "PROPOSAL HANDLER => Report:\n%s",
            report.model_dump_json(indent=2),
        )

        if len(report.errors) > 0:
            logger.warning(
                "PROPOSAL HANDLER => Proposal object has errors, retrying creation."
            )

            proposal_object, report = await self.check_and_retry_proposal_object(
                analyze_result=analyze_result,
                proposal_str=proposal_str,
                proposal_object=proposal_object,
                proposal_validation=report,
            )

        logger.info(
            "PROPOSAL HANDLER => Final cost: %s",
            cost_tracker.cost.model_dump_json(indent=2),
        )

        return proposal_object, report, proposal_str

    async def check_and_retry_proposal_object(
        self,
        analyze_result: AnalyzeResult,
        proposal_str: str,
        proposal_object: ProposalWithPolygonAndValidation,
        proposal_validation: ValidationReport,
    ) -> Tuple[ProposalWithPolygonAndValidation, ValidationReport]:
        """
        Retry creating the proposal object if the first attempt fails.
        """

        proposal_retry = ProposalRetry(cost_tracker=CostTracker())

        new_proposal_object = await proposal_retry.retry_create_proposal_object(
            proposal_str=proposal_str,
            proposal_object=proposal_object,
            proposal_validation=proposal_validation,
        )

        if not new_proposal_object:
            logger.error(
                "PROPOSAL HANDLER => Failed to create a valid proposal object after retry."
            )

            raise ValueError("Failed to create a valid proposal object after retry.")

        new_proposal_with_polygon: ProposalWithPolygonAndValidation = (
            ProposalPolygonHandler(
                proposal_object=new_proposal_object,
                analyze_result=analyze_result,
            ).add_polygon_to_products()
        )
        new_proposal_object, new_report = await self.validate_proposal_object(
            proposal_object=new_proposal_with_polygon
        )

        logger.info(
            "PROPOSAL HANDLER => New proposal report after retry: %s",
            new_report.model_dump_json(indent=2),
        )

        return new_proposal_object, new_report

    async def validate_proposal_object(
        self, proposal_object: Devis | ProposalWithPolygonAndValidation
    ) -> Tuple[ProposalWithPolygonAndValidation, ValidationReport]:
        """
        Evaluate the proposal object and return it.
        """

        proposal, validation_report = ProposalObjectHandler(
            proposal_object=proposal_object
        ).validate_proposal_object()

        return proposal, validation_report
