"""Validate a proposal object (Devis) and return a validation report."""

from __future__ import annotations

import math

from typing import Dict, List, Tuple

from dataclasses import dataclass

from zmq import Enum

from pydantic import BaseModel

from app.proposal_object.schemas import (
    TVA,
    Devis,
    ProductWithPolygonAndValidation,
    ProposalWithPolygonAndValidation,
)


TVA_RATES: Dict[TVA, float] = {
    TVA.TVA_20: 0.20,
    TVA.TVA_10: 0.10,
    TVA.TVA_5_5: 0.055,
    TVA.TVA_2_1: 0.021,
    TVA.TVA_0: 0.0,
}

EPSILON = 0.1


@dataclass
class Totals:
    """Represent the total HT, TVA, and TTC for a proposal object."""

    ht: float = 0.0

    tva: float = 0.0

    @property
    def ttc(self) -> float:  # noqa: D401 – simple prop
        """Calculate the total TTC (HT + TVA)."""

        return round(self.ht + self.tva, 2)

    def __iadd__(self, other: "Totals") -> "Totals":
        """Add another Totals instance to this one."""

        self.ht += other.ht

        self.tva += other.tva

        return self

    def round(self) -> "Totals":  # noqa: D401
        """Round the totals to 2 decimal places."""

        self.ht = round(self.ht, 2)

        self.tva = round(self.tva, 2)

        return self


class IncoherenceKind(str, Enum):
    """Enum representing the kind of incoherence found during validation."""

    PRODUCT_HT_MISMATCH = "product_ht_mismatch"

    PRODUCT_TVA_MISMATCH = "product_tva_mismatch"

    PRODUCT_TTC_MISMATCH = "product_ttc_mismatch"

    PRODUCT_EXTRA_COST = "product_extra_cost"

    TOTAL_HT_MISMATCH = "total_ht_mismatch"

    TOTAL_TVA_MISMATCH = "total_tva_mismatch"

    TOTAL_TTC_MISMATCH = "total_ttc_mismatch"

    TOTAL_EXTRA_COST_MISMATCH = "total_extra_cost_mismatch"


class ValidationError(BaseModel):
    """
    Represents an error found during the validation of a proposal object.
        This error is associated with a specific path in the proposal object and a kind of incoherence.
        It also includes a log message for debugging purposes.
    """

    path: str

    kind: IncoherenceKind

    log: str


class ValidationReport(BaseModel):
    """Report the results of the proposal object validation."""

    computed_total_ht: float

    computed_total_tva: float

    computed_total_ttc: float

    computed_total_cout_additionnel: float

    logs: List[str]

    errors: List[ValidationError]

    def __iter__(self):
        """Iterate over the report items for easy access."""
        yield from self.model_dump().items()


class ValidateProposalObject:
    """Validate a proposal object (Devis) and return a validation report."""

    def validate_proposal_object(
        self, devis: ProposalWithPolygonAndValidation | Devis
    ) -> Tuple[ProposalWithPolygonAndValidation, ValidationReport]:
        """Check recursively the prices in a proposal object (Devis) and return a validation report."""

        if isinstance(devis, Devis):
            devis = ProposalWithPolygonAndValidation(**devis.model_dump())

        logs: List[str] = ["📑 Démarrage de la vérification des prix pour le devis :"]

        errors: List[ValidationError] = []

        totals = Totals()

        add_total = 0.0

        for prod in devis.devis_produits:
            prod_totals, prod_add = self._validate_product(
                prod, path="", level=0, logs=logs, errors=errors
            )

            totals += prod_totals

            add_total += prod_add

        totals.round()

        logs.append(
            f"🔍 Coût additionnel total déclaré = {devis.devis_eco_participation}"
        )

        logs.append(f"🧮 Coût additionnel total calculé = {add_total}")

        if not self._is_close(devis.devis_eco_participation or 0.0, add_total):
            msg = (
                "❌ Écart coût additionnel total : "
                f"déclaré {devis.devis_eco_participation} ↔ calculé {add_total}"
            )

            devis.issue_additional_cost = msg

            errors.append(
                ValidationError(
                    path="__root__",
                    kind=IncoherenceKind.TOTAL_EXTRA_COST_MISMATCH,
                    log=msg,
                )
            )

            logs.append(msg)

        else:
            logs.append("✅ Coût additionnel total cohérent")

        if devis.devis_eco_participation:
            totals.ht += devis.devis_eco_participation

            totals.round()

            devis.issue_additional_cost = None

        logs += [
            f"🏁 HT total calculé du devis = {totals.ht:.2f}",
            f"🏁 TVA totale calculée du devis = {totals.tva:.2f}",
            f"🏁 TTC total calculé du devis = {totals.ttc:.2f}",
        ]

        self._compare_global(devis, "HT", devis.devis_total_ht, totals.ht, logs, errors)

        self._compare_global(
            devis, "TVA", devis.devis_total_tva, totals.tva, logs, errors
        )

        self._compare_global(
            devis, "TTC", devis.devis_total_ttc, totals.ttc, logs, errors
        )

        report = ValidationReport(
            computed_total_ht=totals.ht,
            computed_total_tva=totals.tva,
            computed_total_ttc=totals.ttc,
            computed_total_cout_additionnel=add_total,
            logs=logs,
            errors=errors,
        )

        return devis, report

    def _validate_product(
        self,
        prod: ProductWithPolygonAndValidation,
        path: str,
        level: int,
        logs: List[str],
        errors: List[ValidationError],
    ) -> Tuple[Totals, float]:
        """Validate a single product and its children recursively."""

        indent = "    " * level

        full_path = f"{path}{prod.label}"

        declared_ht = round(prod.price_unitaire_ht * prod.quantite, 2)

        rate = TVA_RATES[prod.tva]

        extra = prod.eco_participation or 0.0

        if prod.sous_produits:
            logs.append(
                f"{indent}🔽 Entrée dans « {full_path} » (HT déclaré = {declared_ht:.2f})"
            )

            branch_totals = Totals()

            add_branch = extra

            for child in prod.sous_produits:
                child_tot, child_add = self._validate_product(
                    child,
                    path=full_path + " > ",
                    level=level + 1,
                    logs=logs,
                    errors=errors,
                )

                branch_totals += child_tot

                add_branch += child_add

            branch_totals.round()

            if branch_totals.ht == 0 and branch_totals.tva == 0:
                logs.append(
                    f"{indent}ℹ️  Somme enfants = 0 € HT et 0 € TVA → "
                    f"on valide « {full_path} » avec HT déclaré ({declared_ht:.2f})"
                )
                tva_amount = round(declared_ht * rate, 2)

                prod.issue = None

                return Totals(ht=declared_ht, tva=tva_amount), add_branch

            self._compare_local(
                full_path, declared_ht, branch_totals.ht, indent, logs, errors, prod
            )

            logs.append(
                f"{indent}💶 TVA cumulée enfants = {branch_totals.tva:.2f} (conteneur TVA ignorée)"
            )
            logs.append(f"{indent}🔼 Sortie de « {full_path} »\n")

            return Totals(
                ht=branch_totals.ht or declared_ht, tva=branch_totals.tva
            ), add_branch

        tva_amount = round(declared_ht * rate, 2)

        logs.append(
            f"{indent}📋 Feuille « {full_path} » : HT = {declared_ht:.2f}, TVA = {tva_amount:.2f}"
        )

        return Totals(ht=declared_ht, tva=tva_amount), extra

    def _compare_local(
        self,
        label: str,
        declared_ht: float,
        children_ht: float,
        indent: str,
        logs: List[str],
        errors: List[ValidationError],
        prod: ProductWithPolygonAndValidation,
    ) -> None:
        """Compare le HT déclaré d’un conteneur avec la somme de ses enfants.

        - Si le HT déclaré est à 0 €, on ignore la comparaison (cas prévu) et
        on considère l’entrée comme *cohérente*.
        - Sinon, on applique la tolérance EPSILON habituelle.
        """

        if math.isclose(declared_ht, 0.0, abs_tol=0):
            logs.append(
                f"{indent}ℹ️  HT parent « {label} » = 0 € → on prend la somme des enfants "
                f"({children_ht:.2f})"
            )

            prod.issue = None

            return

        if not self._is_close(declared_ht, children_ht):
            msg = (
                f"{indent}❌ Écart HT à « {label} » : déclaré {declared_ht:.2f} ↔ "
                f"somme enfants {children_ht:.2f}"
            )

            prod.issue = msg

            errors.append(
                ValidationError(
                    path=label,
                    kind=IncoherenceKind.PRODUCT_HT_MISMATCH,
                    log=msg,
                )
            )

            logs.append(msg)

        else:
            logs.append(f"{indent}✅ HT cohérent pour « {label} »")

            prod.issue = None

    def _compare_global(
        self,
        devis: ProposalWithPolygonAndValidation,
        kind: str,
        declared_val: float,
        computed_val: float,
        logs: List[str],
        errors: List[ValidationError],
    ) -> None:
        label_map = {"HT": "HT", "TVA": "TVA", "TTC": "TTC"}

        logs.append(f"🔍 {label_map[kind]} déclaré = {declared_val:.2f}")

        if not self._is_close(declared_val, computed_val):
            msg = f"❌ Écart {label_map[kind]} global : déclaré {declared_val:.2f} ↔ calculé {computed_val:.2f}"

            errors.append(
                ValidationError(
                    path="__root__",
                    kind=getattr(IncoherenceKind, f"TOTAL_{kind}_MISMATCH"),
                    log=msg,
                )
            )

            logs.append(msg)

            if kind == "HT":
                devis.issue_ht = msg
            elif kind == "TVA":
                devis.issue_tva = msg
            elif kind == "TTC":
                devis.issue_ttc = msg

        else:
            logs.append(f"✅ {label_map[kind]} global cohérent")

            if kind == "HT":
                devis.issue_ht = None
            elif kind == "TVA":
                devis.issue_tva = None
            elif kind == "TTC":
                devis.issue_ttc = None

    def _is_close(self, a: float, b: float) -> bool:
        """Return *True* if |a-b| <= EPSILON (tolerance)."""

        return math.isclose(a, b, abs_tol=EPSILON)
