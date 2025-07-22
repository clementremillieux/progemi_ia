"""Proposal Section Analysis Module."""

from typing import Optional, List

from openai import AsyncOpenAI

from pydantic import BaseModel, Field

from app.cost.cost import CostTracker

from app.utils.utils import token_counter

from config.logger_config import logger

from config.config import env_param

PROPOSAL_SECTION_ANALYZER_SYSTEM_PROMPT = (
    "Vous êtes le meilleur analyseur de devis du monde. "
    "Vous devez analyser un devis au format markdown pour déterminer la structure des catégories de produits de celui-ci, c'est-à-dire les différentes sections et sous-sections des produits du devis. "
    "Vous devez vérifier que le prix total de la catégorie correspond bien au prix des produits listés dans la catégorie. Respectez la structure originale du devis, ne tentez pas de fusionner des lignes. "
    "Ne comptez pas les nouvelles pages comme une nouvelle section. "
    "Ne comptez les éco contributions, éco taxes, éco participations, etc. que si elles sont listées dans le devis. "
    "N'inventez aucune ligne."
)


class NoeudStructureProduitsDevis(BaseModel):
    """
    Représente la structure des produits du devis.
    """

    nom: str = Field(
        ...,
        description="Nom du noeud de la structure des produits du devis",
    )

    sous_groupes_produits: Optional[List["NoeudStructureProduitsDevis"]] = Field(
        None,
        description="Liste des sous-groupes des produits du devis",
    )


class StructureProduitsDevis(BaseModel):
    """Représente la structure des produits du devis."""

    groupes_produits: Optional[List["NoeudStructureProduitsDevis"]] = Field(
        None,
        description="Une ou plusieurs groupes de produits du devis. Si il n'y a qu'un seul groupe, la liste est vide.",
    )


class ProposalSectionAnalysis:
    """Class to handle proposal section analysis."""

    def __init__(
        self, proposal_str: str, cost_tracker: CostTracker, file_base64: str
    ) -> None:
        """Initialize with the path to the proposal."""
        self.proposal_str = proposal_str

        self.cost_tracker = cost_tracker

        self.file_base64 = file_base64

        self.model = "gpt-4.1"

        self.client = AsyncOpenAI(api_key=env_param.OPENAI_API_KEY)

    async def get_sections(self) -> Optional[StructureProduitsDevis]:
        """Get the structured sections of the proposal."""

        logger.debug("SECTION ANALYSIS => Starting proposal section analysis...")

        logger.debug(
            "SECTION ANALYSIS => Proposal token: %s",
            token_counter(self.proposal_str),
        )

        completion = await self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": PROPOSAL_SECTION_ANALYZER_SYSTEM_PROMPT,
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "file",
                            "file": {
                                "filename": "devis.pdf",
                                "file_data": f"data:application/pdf;base64,{self.file_base64}",
                            },
                        },
                        {"type": "text", "text": self.proposal_str},
                    ],
                },
            ],
            tools=[],
            store=False,
            response_format=StructureProduitsDevis,
            temperature=0.0,
        )

        proposal_structure: Optional[StructureProduitsDevis] = completion.choices[
            0
        ].message.parsed

        self.cost_tracker.add_openai_query(
            model=self.model,
            nb_input_token=completion.usage.prompt_tokens,
            nb_output_token=completion.usage.completion_tokens,
            function_name="proposal_section_analyzer",
        )

        if not proposal_structure:
            logger.warning(
                "SECTION ANALYSIS => No proposal structure found in the response."
            )

            return None

        logger.info(
            "SECTION ANALYSIS => Proposal structure: %s",
            proposal_structure.model_dump_json(indent=2),
        )

        logger.info(
            "SECTION ANALYSIS => Cost : %s",
            self.cost_tracker.cost.model_dump_json(indent=2),
        )

        return proposal_structure
