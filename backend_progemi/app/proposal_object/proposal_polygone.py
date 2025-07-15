"""Class to handle proposal polygons for visualization."""

from typing import List, Tuple

from difflib import SequenceMatcher

from azure.ai.documentintelligence.models import (
    AnalyzeResult,
)

from app.proposal_object.schemas import (
    Devis,
    ProposalWithPolygonAndValidation,
    Produit,
    ProductWithPolygonAndValidation,
)

from config.logger_config import logger


class ProposalPolygonHandler:
    """Class to handle proposal polygons for visualization."""

    def __init__(self, proposal_object: Devis, analyze_result: AnalyzeResult) -> None:
        self.proposal_object: Devis = proposal_object

        self.analyze_result: AnalyzeResult = analyze_result

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize a string by removing non-alphanumeric characters and converting to lowercase."""

        return "".join(ch for ch in text.lower() if ch.isalnum())

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        """Calculate the similarity ratio between two strings."""

        return SequenceMatcher(None, a, b).ratio()

    def _best_matching_line_polygon(self, norm_label: str) -> Tuple[List[float], int]:
        """Find the best matching line polygon for a normalized label."""

        best_score = 0.0

        best_polygon: List[float] = []

        page_associated: int = 0

        for page in self.analyze_result.pages or []:
            for line in page.lines or []:
                if not line.polygon:
                    continue

                score = self._similarity(norm_label, self._normalize(line.content))

                if score > best_score:
                    best_score = score

                    best_polygon = line.polygon

                    page_associated = page.page_number

        return best_polygon, page_associated

    def add_polygon_to_product(
        self, produit: Produit
    ) -> ProductWithPolygonAndValidation:
        """Create a ProductWithPolygonAndValidation from a Produit, adding the best matching polygon."""

        polygon, page_associated = self._best_matching_line_polygon(
            self._normalize(produit.label) + self._normalize(produit.description)
        )

        sous_prods_with_poly: List[ProductWithPolygonAndValidation] = []

        if produit.sous_produits:
            sous_prods_with_poly = [
                self.add_polygon_to_product(sp) for sp in produit.sous_produits
            ]

        if not polygon:
            logger.warning(
                "POLYGON HANDLER => Aucun polygone trouvé pour le produit '%s'.",
                produit.label,
            )

            polygon = []

        return ProductWithPolygonAndValidation(
            **produit.model_dump(exclude={"sous_produits"}),
            polygon=polygon,
            page=page_associated,
            sous_produits=sous_prods_with_poly,
        )

    def add_polygon_to_products(self) -> ProposalWithPolygonAndValidation:
        """Add polygons to all products in the proposal object."""

        products_with_polygon = [
            self.add_polygon_to_product(p) for p in self.proposal_object.devis_produits
        ]

        return ProposalWithPolygonAndValidation(
            **self.proposal_object.model_dump(exclude={"devis_produits"}),
            devis_produits=products_with_polygon,
        )
