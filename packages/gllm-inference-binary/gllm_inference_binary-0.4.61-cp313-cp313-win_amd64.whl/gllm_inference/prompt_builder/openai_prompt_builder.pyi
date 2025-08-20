from _typeshed import Incomplete
from gllm_inference.prompt_builder.prompt_builder import BasePromptBuilder as BasePromptBuilder
from gllm_inference.prompt_formatter import OpenAIPromptFormatter as OpenAIPromptFormatter
from gllm_inference.schema import PromptRole as PromptRole

DEPRECATION_MESSAGE: str
OPENAI_MODEL_LIST: Incomplete

class OpenAIPromptBuilder(BasePromptBuilder):
    """A prompt builder for OpenAI models, ensuring compatibility and formatting of prompts.

    The `OpenAIPromptBuilder` class is designed to create prompts compatible with specific OpenAI models. It formats
    the prompt templates by prefixing each template with its role (converted to title case) and concatenating them
    into a single prompt string.

    Attributes:
        system_template (str): The system prompt template. May contain placeholders enclosed in curly braces `{}`.
        user_template (str): The user prompt template. May contain placeholders enclosed in curly braces `{}`.
        prompt_key_set (set[str]): A set of expected keys that must be present in the prompt templates.
        ignore_extra_keys (bool): Whether to ignore extra keys when formatting the prompt.
        formatter (OpenAIPromptFormatter): The formatter to be used to format the prompt into a string in the
            `format_as_string` method.
    """
    formatter: Incomplete
    def __init__(self, system_template: str = '', user_template: str = '', ignore_extra_keys: bool = False) -> None:
        """Initializes a new instance of the OpenAIPromptBuilder class.

        Args:
            system_template (str, optional): The system prompt template. May contain placeholders enclosed in curly
                braces `{}`. Defaults to an empty string.
            user_template (str, optional): The user prompt template. May contain placeholders enclosed in curly
                braces `{}`. Defaults to an empty string.
            ignore_extra_keys (bool, optional): Whether to ignore extra keys when formatting the prompt.
                Defaults to False.
        """
