"""Handles proposal lines for the proposal object."""

from typing import List

from pydantic import BaseModel

from app.proposal_object.schemas import Devis, TVA, Produit


class ProposalLine(BaseModel):
    """One line of a proposal"""

    pack: str

    tva: TVA

    label: str

    description: str

    quantity: float

    quantity_unit: str

    unit_price_ht: float

    @property
    def line(self) -> str:
        """Get the line as a formatted string."""

        return (
            f"{self.pack}; {self.label} - {self.description}, "
            f"{self.quantity} {self.quantity_unit}, {self.unit_price_ht} € HT / unitée, "
            f"Total HT: {self.quantity * self.unit_price_ht} € "
            f"TVA: {self.tva} %"
        )


class ProposalLinesHandler:
    """Class to handle proposal lines for a proposal object."""

    def __init__(self, proposal_object: Devis) -> None:
        self.proposal_object: Devis = proposal_object

    def _collect_lines(self, prod: Produit, buffer: List[ProposalLine]) -> None:
        """Recursively collect all proposal lines from a product and its sub-products."""

        buffer.append(
            ProposalLine(
                pack=prod.lot,
                tva=prod.tva,
                label=prod.label,
                description=prod.description,
                quantity=prod.quantite,
                quantity_unit=prod.unitee_quantite or "",
                unit_price_ht=prod.price_unitaire_ht,
            )
        )

        for child in prod.sous_produits or []:
            self._collect_lines(child, buffer)

    def get_lines(self) -> List[ProposalLine]:
        """Return every product (at all levels) as ProposalLine objects."""

        lines: List[ProposalLine] = []

        for prod in self.proposal_object.devis_produits:
            self._collect_lines(prod, lines)

        return lines

    def get_lines_as_text_array(self, lines: List[ProposalLine]) -> str:
        """Return a nicely formatted text array named `arraybcimunnm`."""

        headers = [
            "PACK",
            "TVA",
            "LABEL",
            "DESCRIPTION",
            "QTY",
            "UNIT",
            "UNIT_PRICE_HT",
            "TOTAL_HT",
        ]

        rows: list[list[str]] = []

        for l in lines:
            rows.append(
                [
                    str(getattr(l.pack, "value", l.pack)),  # Enum → valeur
                    str(getattr(l.tva, "value", l.tva)),
                    l.label,
                    l.description,
                    f"{l.quantity:g}",
                    l.quantity_unit or "",
                    f"{l.unit_price_ht:.2f}",
                    f"{l.quantity * l.unit_price_ht:.2f}",
                ]
            )

        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(cell))

        def _fmt_row(row: list[str]) -> str:
            return (
                "| "
                + " | ".join(cell.center(col_widths[i]) for i, cell in enumerate(row))
                + " |"
            )

        header_line = _fmt_row(headers)

        separator = "|-" + "-|-".join("-" * w for w in col_widths) + "-|"

        data_lines = [_fmt_row(r) for r in rows]

        joined_lines = [header_line, separator, *data_lines]

        content = ",\n    ".join(f'"{l}"' for l in joined_lines)

        return f"arraybcimunnm = [\n    {content}\n]"
