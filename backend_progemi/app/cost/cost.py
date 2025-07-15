"""Cost tracker module."""

from typing import List, Tuple

from decimal import ROUND_HALF_UP, Decimal

from app.cost.schemas import Cost, Query


_MODEL_PRICES: List[Tuple[str, tuple[float, float]]] = [
    ("gpt-4o-mini", (0.150, 0.60)),
    ("gpt-4o-", (2.50, 10.00)),
    ("gpt-4.1-mini", (0.40, 1.60)),
    ("gpt-4.1", (2.00, 8.00)),
    ("o3", (2.00, 8.00)),
    ("o4-mini", (1.10, 4.40)),
]


_EMBEDDING_PRICES: dict[str, float] = {
    "text-embedding-3-large": 0.13,
}


def _round(value: float | Decimal) -> float:
    """Uniform rounding to 6 decimals (bankers rounding)."""

    return float(Decimal(value).quantize(Decimal("0.000001"), ROUND_HALF_UP))


def _find_prices(model: str) -> Tuple[float, float]:
    """Return (input_price, output_price) for **model**.

    Raises:
        ValueError: if the model is unknown.
    """

    for prefix, prices in _MODEL_PRICES:
        if model.startswith(prefix):
            return prices

    raise ValueError(f"Unknown model family for '{model}'. Update _MODEL_PRICES.")


class CostTracker:
    """Aggregate and expose cost information."""

    def __init__(self) -> None:
        self.cost: Cost = Cost()

    def add_openai_query(
        self,
        *,
        nb_input_token: int | None,
        nb_output_token: int | None,
        model: str,
        function_name: str | None = None,
    ) -> None:
        """Record a chat/completion API call.

        Args:
            nb_input_token: Prompt tokens.
            nb_output_token: Completion tokens.
            model: Model name (e.g. "gpt-4o-mini-2025-05-13").
            function_name: Optional label (makes dashboards nicer).
        """

        input_price, output_price = _find_prices(model)

        cost_input = (input_price * (nb_input_token or 0)) / 1_000_000

        cost_output = (output_price * (nb_output_token or 0)) / 1_000_000

        total_cost = cost_input + cost_output

        self.cost.cost_openai.cost_openai_input += _round(cost_input)

        self.cost.cost_openai.cost_openai_output += _round(cost_output)

        self.cost.cost_openai.cost_openai_total += _round(total_cost)

        self.cost.cost += _round(total_cost)

        self.cost.cost_openai.nb_query += 1

        self.cost.cost_openai.queries.append(
            Query(model=model, cost=_round(total_cost), function_name=function_name)
        )

    def add_embeddings_query(
        self,
        *,
        nb_token: int,
        model: str,
        function_name: str | None = None,
    ) -> None:
        """Record an embeddings API call."""

        if model not in _EMBEDDING_PRICES:
            raise ValueError(f"Unknown embedding model '{model}'.")

        cost_embeddings = (_EMBEDDING_PRICES[model] * nb_token) / 1_000_000

        rounded = _round(cost_embeddings)

        self.cost.cost_openai.cost_embeddings += rounded

        self.cost.cost_openai.cost_openai_total += rounded

        self.cost.cost += rounded

        self.cost.cost_openai.nb_query += 1

        self.cost.cost_openai.queries.append(
            Query(model=model, cost=rounded, function_name=function_name)
        )

    def init_tracker_value(self, euro_cost: float, openai_cost: float) -> None:
        """Initialize tracker from persisted values (e.g. after restart)."""

        self.cost.cost = euro_cost

        self.cost.cost_openai.cost_openai_total = openai_cost

    def as_dict(self) -> dict:
        """Return a JSON‑serializable snapshot (no Pydantic needed upstream)."""

        return self.cost.model_dump()
