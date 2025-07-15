"""Proposal object (Devis) handler"""

from typing import Tuple


from app.proposal_object.proposal_evaluate_result import (
    EvaluateProposalObject,
    EvaluationResult,
)

from app.proposal_object.proposal_validate_results import (
    ValidateProposalObject,
    ValidationReport,
)

from app.proposal_object.proposal_lines import ProposalLinesHandler

from app.proposal_object.proposal_object_to_text import ProposalObjectToText

from app.proposal_object.schemas import Devis, ProposalWithPolygonAndValidation


class ProposalObjectHandler:
    """Class to handle proposal objects (Devis)."""

    def __init__(
        self, proposal_object: Devis | ProposalWithPolygonAndValidation
    ) -> None:
        """Initialize the proposal object handler with paths."""

        self.proposal_object: Devis | ProposalWithPolygonAndValidation = proposal_object

    def convert_to_text(self) -> str:
        """Convert the proposal object to a text representation."""

        proposal_text = ProposalObjectToText(self.proposal_object, "€").format()

        return proposal_text

    # def convert_to_pdf(self) -> None:
    #     """Convert the proposal object to a PDF representation."""

    #     ProposalObjectToPDF(self.proposal_object, "€").build(
    #         Path(self.proposal_path.proposal_pdf_object_path)
    #     )

    def convert_to_proposal_lines(self) -> str:
        """Convert the proposal object to proposal lines and log the results."""

        proposal_lines_handler = ProposalLinesHandler(self.proposal_object)

        proposal_lines = proposal_lines_handler.get_lines()

        lines_str = proposal_lines_handler.get_lines_as_text_array(proposal_lines)

        return lines_str

    def validate_proposal_object(
        self,
    ) -> Tuple[ProposalWithPolygonAndValidation, ValidationReport]:
        """Validate the proposal object and log the results."""

        proposal, validate_report = ValidateProposalObject().validate_proposal_object(
            devis=self.proposal_object
        )

        return proposal, validate_report

    def evaluate_proposal_object(self, proposal_expected: Devis) -> EvaluationResult:
        """Evaluate the proposal object against expected values and write JSON + logs."""

        evaluation: EvaluationResult = EvaluateProposalObject(
            expected=proposal_expected, predicted=self.proposal_object
        ).evaluate()

        return evaluation

    def analyze_proposal_object(self) -> None:
        """Analyze the proposal object and log the results."""

        self.convert_to_text()

        # self.convert_to_pdf()

        self.convert_to_proposal_lines()

        self.validate_proposal_object()

        # self.evaluate_proposal_object()
