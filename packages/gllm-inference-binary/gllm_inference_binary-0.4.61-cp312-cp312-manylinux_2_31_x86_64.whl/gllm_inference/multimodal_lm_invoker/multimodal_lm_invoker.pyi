import abc
from _typeshed import Incomplete
from abc import ABC
from gllm_core.event import EventEmitter as EventEmitter
from gllm_inference.constants import MESSAGE_TUPLE_LENGTH as MESSAGE_TUPLE_LENGTH
from typing import Any, Generic

InputType: Incomplete
OutputType: Incomplete

class BaseMultimodalLMInvoker(ABC, Generic[InputType, OutputType], metaclass=abc.ABCMeta):
    """A base class for multimodal language model invokers used in Gen AI applications.

    The `BaseMultimodalLMInvoker` class provides a framework for invoking multimodal language models with the provided
    prompt and hyperparameters. The prompt may contain multimodal inputs that is defined by the type variable
    `InputType`, while the multimodal output is defined by the type variable `OutputType`. It handles both standard
    and streaming invocation.

    Attributes:
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the multimodal language model.
    """
    default_hyperparameters: Incomplete
    def __init__(self, default_hyperparameters: dict[str, Any] | None = None) -> None:
        """Initializes a new instance of the BaseMultimodalLMInvoker class.

        Args:
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the
                multimodal language model. Defaults to None, in which case an empty dictionary is used.
        """
    async def invoke(self, prompt: list[tuple[str, list[InputType]]], hyperparameters: dict[str, Any] | None = None, event_emitter: EventEmitter | None = None) -> OutputType:
        """Invokes the multimodal language model with the provided prompt and hyperparameters.

        This method validates the prompt and invokes the multimodal language model with the provided prompt and
        hyperparameters. The prompt may contain multimodal inputs that is defined by the type variable `InputType`.
        It handles both standard and streaming invocation. Streaming mode is enabled if an event emitter is provided.

        Args:
            prompt (list[tuple[str, list[InputType]]]): The input prompt as a list of tuples containing a role-content
                list pair. The content list may contain multimodal inputs that is defined by the type variable
                `InputType`.
            hyperparameters (dict[str, Any] | None, optional): A dictionary of hyperparameters for the multimodal
                language model. Defaults to None, in which case the default hyperparameters are used.
            event_emitter (EventEmitter | None, optional): The event emitter for streaming tokens. If provided,
                streaming invocation is enabled. Defaults to None.

        Returns:
            OutputType: The generated response from the multimodal language model.

        Raises:
            ValueError: If the prompt is not in the correct format.
        """
