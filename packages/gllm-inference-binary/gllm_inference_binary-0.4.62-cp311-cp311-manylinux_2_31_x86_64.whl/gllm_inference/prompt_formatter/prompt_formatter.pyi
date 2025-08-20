import abc
from _typeshed import Incomplete
from abc import ABC
from gllm_inference.schema import MultimodalContent as MultimodalContent, MultimodalPrompt as MultimodalPrompt, PromptRole as PromptRole

class BasePromptFormatter(ABC, metaclass=abc.ABCMeta):
    """A base class for prompt formatters used in Gen AI applications.

    The prompt formatter class is used to format a prompt into a string with specific formatting.

    Attributes:
        content_separator (str): The separator to be used between the string in a single message.
    """
    content_separator: Incomplete
    def __init__(self, content_separator: str = '\n') -> None:
        '''Initializes a new instance of the BasePromptFormatter class.

        Args:
            content_separator (str, optional): The separator to be used between the string in a single message.
                Defaults to "\\n".
        '''
    def format(self, prompt: MultimodalPrompt) -> str:
        """Formats the prompt as a string.

        Args:
            prompt (MultimodalPrompt): The prompt to be formatted as a string.

        Returns:
            str: The formatted prompt as a string.
        """
