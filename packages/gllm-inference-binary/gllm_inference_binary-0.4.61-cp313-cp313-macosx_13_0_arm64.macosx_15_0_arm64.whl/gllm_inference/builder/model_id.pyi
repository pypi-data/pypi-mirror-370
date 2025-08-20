from _typeshed import Incomplete
from gllm_inference.schema.model_id import ModelId as _ModelId
from typing import Any

logger: Incomplete

class ModelId(_ModelId):
    """Deprecated: Use gllm_inference.schema.ModelId instead."""
    @classmethod
    def from_string(cls, *args: Any, **kwargs: Any) -> None:
        """Deprecated: Use gllm_inference.schema.ModelId.from_string instead."""

ModelProvider: Incomplete
