"""Proposal Text Analysis Module."""

from typing import List, Optional, Type

from langchain.schema import BaseMessage, HumanMessage, SystemMessage

from openai.types.chat.chat_completion_prediction_content_param import (
    ChatCompletionPredictionContentParam,
)

from app.agent.agent import Agent

from app.cost.cost import CostTracker

from app.proposal_object.schemas import Devis

from config.config import env_param

from config.logger_config import logger

PROPOSAL_ANALYZER_SYSTEM_PROMPT = (
    "Vous êtes le meilleur analyseur de devis du monde. Vous devez reconstruire le devis à partir d'un texte brut. "
    "Pour chaque produit du devis, vous devez très précisément noter son label, sa description, le lot auquel il appartient, son prix HT unitaire, la quantité, l'unité, la TVA et les possibles coûts supplémentaires. "
    "Les produits peuvent être groupés par catégories et ou contenir des sous-catégories de produits imbriquées. "
    "1 - Trouvez la structure exacte de chaque catégorie du devis. "
    "2 - Vérifiez que le prix total de la catégorie correspond bien au prix des produits listés dans la catégorie."
    "3 - Respectez la structure originale du devis, ne tentez pas de fusionner des lignes. "
    "4 - Ne comptez pas les nouvelles pages comme une nouvelle section. "
    "5 - N'inventez aucune ligne. "
)


class ProposalTextAnalyzer:
    """Proposal text analyzer"""

    def __init__(self, cost_tracker: CostTracker) -> None:
        """Initialize the proposal analyzer with the OpenAI API key and model."""

        self.model = "gpt-4.1"

        self.agent: Agent = Agent(
            api_key=env_param.OPENAI_API_KEY,
            model_name=self.model,
            system_promt=PROPOSAL_ANALYZER_SYSTEM_PROMPT,
            nb_retry=2,
            temprature=1 if self.model in ["o4-mini", "o3"] else 0,
            timeout=200,
            name="proposal_analyzer",
            cost_tracker=cost_tracker,
            reasoning_effort="high",
        )

        self.cost_tracker: CostTracker = cost_tracker

    async def analyze(
        self, chat_historic: List[BaseMessage], devis_model: Type[Devis]
    ) -> Optional[Devis]:
        """Structure the proposal"""

        proposal_structured: Optional[Devis] = await self.agent.run(
            response_format=devis_model, chat_historic=chat_historic
        )

        return proposal_structured

    async def structure_proposal(
        self, raw_proposal: str, section_analysis: str, devis_model: Type[Devis]
    ) -> Optional[Devis]:
        """Check if the client is spam"""

        chat_historic = [
            SystemMessage(content=PROPOSAL_ANALYZER_SYSTEM_PROMPT),
            HumanMessage(
                "Voici un premier analyse de la sturcutre du devis :\n\n"
                + section_analysis
            ),
            HumanMessage(content=raw_proposal),
        ]

        proposal_structured: Optional[Devis] = await self.analyze(
            chat_historic=chat_historic, devis_model=devis_model
        )

        if proposal_structured is None:
            logger.info("PROPOSAL TEXT ANALYSIS => No structured proposal found.")

            return None

        return proposal_structured

    async def analyze_and_structure(
        self, raw_proposal: str, section_analysis: str, devis_model: Type[Devis]
    ) -> Optional[Devis]:
        """Analyze and structure the proposal text."""

        logger.info("PROPOSAL TEXT ANALYSIS => Starting proposal analysis...")

        structured_proposal: Optional[Devis] = await self.structure_proposal(
            raw_proposal=raw_proposal,
            section_analysis=section_analysis,
            devis_model=devis_model,
        )

        if structured_proposal is None:
            logger.error(
                "PROPOSAL TEXT ANALYSIS => Failed to analyze and structure the proposal."
            )
            return None

        logger.info(
            "PROPOSAL TEXT ANALYSIS => Structured proposal: %s",
            structured_proposal.model_dump_json(indent=2),
        )

        logger.info(
            "PROPOSAL TEXT ANALYSIS => Cost: %s",
            self.cost_tracker.cost.model_dump_json(indent=2),
        )

        return structured_proposal
