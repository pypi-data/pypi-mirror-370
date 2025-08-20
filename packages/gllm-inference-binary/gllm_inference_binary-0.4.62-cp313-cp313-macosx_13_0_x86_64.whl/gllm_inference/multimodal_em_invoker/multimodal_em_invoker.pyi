import abc
from abc import ABC
from gllm_inference.schema import Vector as Vector
from typing import Generic, TypeVar

InputType = TypeVar('InputType')

class BaseMultimodalEMInvoker(ABC, Generic[InputType], metaclass=abc.ABCMeta):
    """A base class for multimodal embedding model invokers used in Gen AI applications.

    The `BaseMultimodalEMInvoker` class provides a framework for invoking multimodal embedding models.
    The input may contain multimodal content that is defined by the type variable `InputType`.

    Attributes:
        None
    """
    async def invoke(self, content: InputType | list[InputType]) -> Vector | list[Vector]:
        """Invokes the multimodal embedding model with the provided content.

        This method validates the content and then invokes the multimodal embedding model by calling the
        `_invoke` method.

        Args:
            content (InputType | list[InputType]): The input content or list of input contents to be embedded using the
                multimodal embedding model. The content may contain multimodal inputs that is defined by the type
                variable `InputType`.

        Returns:
            Vector | list[Vector]: The vector representations of the input content:
                1. If the input is a single content, the output is a `Vector`.
                2. If the input is a list of contents, the output is a `list[Vector]`.

        Raises:
            ValueError: If the content is not of the correct type.
        """
