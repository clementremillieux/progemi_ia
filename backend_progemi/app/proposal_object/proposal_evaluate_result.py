"""Evaluate proposal objects and generate evaluation results."""

from __future__ import annotations

from io import StringIO

from typing import Dict, Sequence

from pydantic import BaseModel, model_validator

from app.proposal_object.schemas import Devis, Produit


class MetadataResult(BaseModel):
    """Metadata about the evaluation process."""

    checked: int

    ok: int

    nok: int

    details: Dict[str, str]


class EntitiesResult(BaseModel):
    """Results of the evaluation of entities in the proposal object."""

    total_actual: int
    total_compared: int
    price_ok: int
    quantity_ok: int
    vat_ok: int
    lot_ok: int
    subcount_ok: int

    percent_entities_compared: float | None = None
    percent_price_ok: float | None = None
    percent_quantity_ok: float | None = None
    percent_vat_ok: float | None = None
    percent_lot_ok: float | None = None
    percent_subcount_ok: float | None = None

    @model_validator(mode="after")
    def _populate_ratios(self):
        """Calculate the percentage ratios for the evaluation results."""

        tc, ta = self.total_compared, self.total_actual or 1

        pct = lambda ok: round(ok / tc * 100, 2) if tc else 0.0

        self.percent_entities_compared = round(tc / ta * 100, 2)
        self.percent_price_ok = pct(self.price_ok)
        self.percent_quantity_ok = pct(self.quantity_ok)
        self.percent_vat_ok = pct(self.vat_ok)
        self.percent_lot_ok = pct(self.lot_ok)
        self.percent_subcount_ok = pct(self.subcount_ok)
        return self


class _Stats:
    """Statistics for the evaluation of proposal objects."""

    def __init__(self, total_actual: int) -> None:
        self.total_actual = total_actual

        self.total_compared = 0

        self.price_ok = 0

        self.quantity_ok = 0

        self.vat_ok = 0

        self.lot_ok = 0

        self.subcount_ok = 0


class EvaluationResult(BaseModel):
    """Result of the evaluation process."""

    metadata: MetadataResult

    entities: EntitiesResult

    logs: str


class EvaluateProposalObject(BaseModel):
    """Evaluate a proposal object (Devis) against expected values."""

    expected: Devis

    predicted: Devis

    class Config:
        """Configuration for the Pydantic model."""

        arbitrary_types_allowed = True

    def evaluate(self) -> EvaluationResult:  # noqa: D401
        """Evaluate the proposal object and return the evaluation result."""

        buffer = StringIO()

        write = lambda s="": buffer.write(s + "\n")

        meta_fields = [
            "devis_total_ht",
            "devis_total_ttc",
            "devis_total_tva",
        ]

        meta_ok = meta_nok = 0

        meta_details: Dict[str, str] = {}

        write("🔎 Vérification des métadonnées :")

        for f in meta_fields:
            exp_val = getattr(self.expected, f)

            pred_val = getattr(self.predicted, f)

            if exp_val == pred_val:
                meta_ok += 1

                meta_details[f] = "✅"

                write(f"  {f}: {exp_val} == {pred_val} ✅")

            else:
                meta_nok += 1

                meta_details[f] = "❌"

                write(f"  {f}: {exp_val} != {pred_val} ❌")

        stats = self._build_entity_stats(self.expected.devis_produits)

        write("\n📦 Comparaison des produits :")

        self._compare_product_lists(
            self.expected.devis_produits,
            self.predicted.devis_produits,
            stats=stats,
            write=write,
            indent=2,
        )

        write("\n📊 Résumé des métriques :")

        self._log_metrics(stats, write)

        metadata_obj = MetadataResult(
            checked=len(meta_fields), ok=meta_ok, nok=meta_nok, details=meta_details
        )
        entities_obj = EntitiesResult(**stats.__dict__)  # type: ignore[arg-type]

        return EvaluationResult(
            metadata=metadata_obj, entities=entities_obj, logs=buffer.getvalue()
        )

    def _build_entity_stats(self, products: Sequence[Produit]) -> _Stats:
        """Build statistics for the entities in the proposal object."""

        return _Stats(total_actual=self._count_entities(products))

    def _count_entities(self, products: Sequence[Produit]) -> int:
        """Count the total number of entities in the product list."""

        return sum(1 + self._count_entities(p.sous_produits or []) for p in products)

    def _compare_product_lists(
        self,
        expected_list: Sequence[Produit],
        predicted_list: Sequence[Produit],
        *,
        stats: _Stats,
        write,
        indent: int,
    ) -> None:
        """Compare two lists of products and log the results."""

        space = " " * indent

        for idx, (pe, pp) in enumerate(zip(expected_list, predicted_list)):
            stats.total_compared += 1

            write(f"{space}▶ Produit[{idx}] ({pe.label}) :")

            self._compare_val(
                pe.price_unitaire_ht,
                pp.price_unitaire_ht,
                "price_ht",
                stats,
                "price_ok",
                write,
                space,
            )

            self._compare_val(
                pe.quantite, pp.quantite, "quantite", stats, "quantity_ok", write, space
            )

            self._compare_val(pe.tva, pp.tva, "tva", stats, "vat_ok", write, space)

            self._compare_val(pe.lot, pp.lot, "lot", stats, "lot_ok", write, space)

            sub_exp, sub_pred = pe.sous_produits or [], pp.sous_produits or []

            if len(sub_exp) == len(sub_pred):
                stats.subcount_ok += 1

                write(
                    f"{space}  - sous_produits count: {len(sub_exp)} == {len(sub_pred)} ✅"
                )

            else:
                write(
                    f"{space}  - sous_produits count: {len(sub_exp)} != {len(sub_pred)} ❌"
                )

            if sub_exp and sub_pred:
                self._compare_product_lists(
                    sub_exp, sub_pred, stats=stats, write=write, indent=indent + 4
                )

    def _compare_val(
        self,
        exp_val,
        pred_val,
        label: str,
        stats: _Stats,
        counter: str,
        write,
        space: str,
    ):
        """Compare two values and log the result."""

        if exp_val == pred_val:
            setattr(stats, counter, getattr(stats, counter) + 1)
            write(f"{space}  - {label}: {exp_val} == {pred_val} ✅")

        else:
            write(f"{space}  - {label}: {exp_val} != {pred_val} ❌")

    def _fmt_metric(self, ok: int, total: int) -> str:
        """Format the metric as a string with percentage and status."""

        pct = round(ok / total * 100, 2) if total else 0.0

        status = "✅" if pct == 100 else "❌"

        return f"{ok}/{total} ({pct}%) {status}"

    def _log_metrics(self, stats: _Stats, write) -> None:
        """Log the metrics from the evaluation statistics."""

        tot = stats.total_actual or 1
        cmp_ = stats.total_compared or 1

        write(f"  - Entités totales           : {tot}")
        write(
            f"  - Entités comparées         : {cmp_} ({round(cmp_ / tot * 100, 2)}%) {'✅' if cmp_ == tot else '❌'}"
        )
        write(
            f"  - Prix OK                   : {self._fmt_metric(stats.price_ok, cmp_)}"
        )
        write(
            f"  - Quantité OK               : {self._fmt_metric(stats.quantity_ok, cmp_)}"
        )
        write(f"  - TVA OK                    : {self._fmt_metric(stats.vat_ok, cmp_)}")
        write(f"  - Lot OK                    : {self._fmt_metric(stats.lot_ok, cmp_)}")
        write(
            f"  - Sous-produits count OK    : {self._fmt_metric(stats.subcount_ok, cmp_)}"
        )
