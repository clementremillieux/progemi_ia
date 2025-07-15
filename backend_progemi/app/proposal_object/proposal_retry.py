"""Retry to generate a proposal object if the first attempt fails."""

from typing import Optional

from openai import AsyncOpenAI

from app.cost.cost import CostTracker

from app.proposal_object.proposal_validate_results import (
    ValidationReport,
)

from app.proposal_object.schemas import Devis, ProposalWithPolygonAndValidation

from config.config import env_param

RETRY_PROMPT = """Regénérez la structure du devis en corrigeant les erreurs de structure suivantes :
{full_errors_str}
Assurez-vous que la structure du devis respecte le format attendu et que les totaux HT, TVA et TTC sont corrects."""


class ProposalRetry:
    """Class to retry proposal object creation."""

    def __init__(self, cost_tracker: CostTracker) -> None:
        """Initialize the ProposalRetry with a cost tracker."""

        self.cost_tracker: CostTracker = cost_tracker

        self.model: str = "gpt-4.1"

        self.client: AsyncOpenAI = AsyncOpenAI(api_key=env_param.OPENAI_API_KEY)

    def get_full_errors_str(self, validation_report: ValidationReport) -> str:
        """Get a string representation of the full errors in the validation report.

        Args:
            validation_report (ValidationReport): The validation report.

        Returns:
            str: A string containing all errors.
        """

        full_errors_str = "\n".join(f"- {error}" for error in validation_report.errors)

        return full_errors_str

    def create_proposal_context(
        self,
        proposal: ProposalWithPolygonAndValidation,
        proposal_str: str,
        full_errors_str: str,
    ) -> str:
        """Create a context for proposal object creation.

        Returns:
            str: The context string.
        """

        wrong_structure = proposal.model_dump_json(
            indent=1, exclude_none=True, exclude={"polygon"}
        )

        context_wrong = f"""# Voici le devis original : {proposal_str}

        # Voici le devis avec les erreurs de structure :
        {wrong_structure}

        # Voici les erreurs de structure du devis :
        {full_errors_str}"""

        return context_wrong

    async def retry_create_proposal_object(
        self,
        proposal_str: str,
        proposal_object: ProposalWithPolygonAndValidation,
        proposal_validation: ValidationReport,
    ) -> Optional[Devis]:
        """
        Retry creating the proposal object if the first attempt fails.

        Args:
            proposal_str (str): The proposal string.
            proposal_object (ProposalWithPolygonAndValidation): The proposal object.
            proposal_validation (ValidationReport): The validation report.

        Returns:
            ProposalWithPolygonAndValidation: The validated proposal object.
        """

        full_errors_str = self.get_full_errors_str(proposal_validation)

        context_wrong = self.create_proposal_context(
            proposal=proposal_object,
            proposal_str=proposal_str,
            full_errors_str=full_errors_str,
        )

        completion = await self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": RETRY_PROMPT.format(
                                full_errors_str=full_errors_str
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": context_wrong},
                    ],
                },
            ],
            tools=[],
            store=False,
            response_format=Devis,
            temperature=0.0,
        )

        new_proposal_object: Optional[Devis] = completion.choices[0].message.parsed

        self.cost_tracker.add_openai_query(
            model=self.model,
            nb_input_token=completion.usage.prompt_tokens,
            nb_output_token=completion.usage.completion_tokens,
            function_name="proposal_section_analyzer",
        )

        return new_proposal_object
