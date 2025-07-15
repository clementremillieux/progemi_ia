"""Converts a proposal object to a PDF file without displaying the description."""

from pathlib import Path

from datetime import datetime

from xml.sax.saxutils import escape

from reportlab.lib import colors

from reportlab.lib.units import mm

from reportlab.lib.pagesizes import A4

from reportlab.lib.enums import TA_LEFT

from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.proposal_object.schemas import Devis, Lot, Produit


class ProposalObjectToPDF:
    """Builds a PDF document from a Devis object."""

    def __init__(self, devis: Devis, currency_symbol: str = "€") -> None:
        self.devis = devis
        self.currency_symbol = currency_symbol
        self.styles = getSampleStyleSheet()
        self.styles.add(
            ParagraphStyle(
                name="LotTitle",
                fontSize=11,
                leading=13,
                spaceBefore=6,
                spaceAfter=4,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="Product",
                parent=self.styles["Normal"],
                fontSize=9,
                leading=11,
                spaceAfter=0,
            )
        )

        for lvl in range(4):
            name = f"ProdLvl{lvl}"
            size = 11 - lvl if lvl < 3 else 9
            bold = lvl == 0
            self.styles.add(
                ParagraphStyle(
                    name=name,
                    parent=self.styles["Normal"],
                    fontName="Helvetica-Bold" if bold else "Helvetica",
                    fontSize=size,
                    leading=size + 2,
                    leftIndent=(lvl * 5) * mm,
                    firstLineIndent=(lvl * 5) * mm,
                    spaceAfter=0,
                    alignment=TA_LEFT,
                )
            )

    def build(self, filepath: str | Path) -> None:
        """Build the PDF document and write it to the specified filepath."""

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            title="Devis",
            author="progemi",
            creationDate=datetime.now(),
        )

        story: list = []

        story.append(Spacer(1, 5 * mm))

        for lot in Lot:
            prods_lot = [p for p in self.devis.devis_produits if p.lot == lot]

            if not prods_lot:
                continue

            story.append(Paragraph(lot.name.replace("_", " "), self.styles["LotTitle"]))

            story.append(self._build_table(prods_lot))

            story.append(Spacer(1, 4 * mm))

        story.append(Spacer(1, 2 * mm))

        story.append(self._build_totals_table())

        doc.build(story)

    def _flatten(self, produit: Produit, level: int = 0) -> list[list[str]]:
        """Flatten a product and its sub-products into a list of rows for the table."""

        style_name = f"ProdLvl{min(level, 3)}"

        label_para = Paragraph(escape(produit.label), self.styles[style_name])

        row = [
            label_para,
            str(produit.quantite),
            self._money(produit.price_unitaire_ht),
            produit.tva.value,
            self._money(produit.quantite * produit.price_unitaire_ht),
        ]

        rows = [row]

        for sp in produit.sous_produits or []:
            rows.extend(self._flatten(sp, level + 1))

        return rows

    def _build_table(self, produits: list[Produit]):
        header = ["Produit", "Qté", "PU HT", "TVA", "Total HT"]

        data = [header]
        for prod in produits:
            data.extend(self._flatten(prod))

        col_widths = [
            80 * mm,
            15 * mm,
            30 * mm,
            20 * mm,
            25 * mm,
        ]

        table = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                ]
            )
        )
        return table

    def _build_totals_table(self):
        """Build a table for the totals of the proposal."""

        data = [
            ["", ""],
            ["Total TVA", self._money(self.devis.devis_total_tva)],
            ["Total HT", self._money(self.devis.devis_total_ht)],
            ["Total TTC", self._money(self.devis.devis_total_ttc)],
        ]

        if self.devis.devis_eco_participation is not None:
            data.insert(
                1, ["Coût additionnel", self._money(self.devis.devis_eco_participation)]
            )

        table = Table(data, colWidths=[70 * mm, 40 * mm], hAlign="RIGHT")

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 1), (-1, 1), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ]
            )
        )

        return table

    def _money(self, value: float) -> str:
        """Format a monetary value as a string."""

        return f"{value:,.2f} {self.currency_symbol}".replace(",", " ").replace(
            ".", ","
        )
