"""Convert a Devis object to a human-readable text format."""

from typing import List

from textwrap import indent

from app.proposal_object.schemas import Devis, Produit


class ProposalObjectToText:
    """Format Devis object into a human-readable string."""

    def __init__(self, devis: Devis, currency_symbol: str = "€") -> None:
        """Init the formatter with a Devis object and an optional currency symbol."""

        self.devis = devis

        self.currency_symbol = currency_symbol

    def format(self) -> str:
        """Format the Devis object into a human-readable string."""

        sections: List[str] = [
            "",
        ]

        for lot in []:
            produits_lot = [p for p in self.devis.devis_produits if p.lot == lot]

            if not produits_lot:
                continue

            sections.append(f"╔══ {lot.name.replace('_', ' ')} ══╗")

            for produit in produits_lot:
                sections.extend(self._format_produit(produit, level=1))

            sections.append("")

        if self.devis.devis_eco_participation is not None:
            sections.append(
                f"Coût additionnel : {self._money(self.devis.devis_eco_participation)}"
            )

        sections.extend(
            [
                f"Total TVA : {self._money(self.devis.devis_total_tva)}",
                f"Total HT  : {self._money(self.devis.devis_total_ht)}",
                f"Total TTC : {self._money(self.devis.devis_total_ttc)}",
            ]
        )

        return "\n".join(sections)

    def _format_produit(self, produit: Produit, level: int = 0) -> List[str]:
        """Format a single product into a list of strings with indentation."""

        indent_spaces = "  " * level

        bullet = f"{indent_spaces}• "

        lines = [
            (
                f"{bullet}{produit.label} (x{produit.quantite}) — "
                f"{self._money(produit.price_unitaire_ht)} HT | {produit.tva.value}"
            )
        ]

        if produit.description:
            lines.append(indent(produit.description, indent_spaces + "  "))

        for sp in produit.sous_produits or []:
            lines.extend(self._format_produit(sp, level + 1))

        return lines

    def _money(self, value: float) -> str:
        """Format a monetary value according to French conventions."""

        return f"{value:,.2f} {self.currency_symbol}".replace(",", " ").replace(
            ".", ","
        )
