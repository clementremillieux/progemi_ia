"""Cost tracker schemas module."""

from typing import List, Optional

from pydantic import BaseModel


class Query(BaseModel):
    """Query schema."""

    model: str

    cost: float

    function_name: Optional[str] = None


class CostOpenAI(BaseModel):
    """Cost openai."""

    cost_openai_input: float = 0

    cost_openai_output: float = 0

    cost_embeddings: float = 0

    cost_openai_total: float = 0

    nb_query: int = 0

    queries: List[Query] = []


class Cost(BaseModel):
    """Cost tracker."""

    cost: float = 0

    cost_openai: CostOpenAI = CostOpenAI()
