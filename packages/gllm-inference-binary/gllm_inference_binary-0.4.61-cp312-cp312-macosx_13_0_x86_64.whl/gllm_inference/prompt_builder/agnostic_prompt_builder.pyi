from _typeshed import Incomplete
from gllm_inference.prompt_builder.prompt_builder import BasePromptBuilder as BasePromptBuilder
from gllm_inference.prompt_formatter import AgnosticPromptFormatter as AgnosticPromptFormatter
from gllm_inference.schema import PromptRole as PromptRole

DEPRECATION_MESSAGE: str

class AgnosticPromptBuilder(BasePromptBuilder):
    """A prompt builder that is agnostic to specific model types and formats prompts with a customizable separator.

    The `AgnosticPromptBuilder` class constructs a prompt by joining the content of the prompt templates using a
    specified separator. It is designed to work independently of specific model types.

    Attributes:
        system_template (str): The system prompt template. May contain placeholders enclosed in curly braces `{}`.
        user_template (str): The user prompt template. May contain placeholders enclosed in curly braces `{}`.
        prompt_key_set (set[str]): A set of expected keys that must be present in the prompt templates.
        ignore_extra_keys (bool): Whether to ignore extra keys when formatting the prompt.
        formatter (AgnosticPromptFormatter): The formatter to be used to format the prompt into a string in the
            `format_as_string` method.
    """
    formatter: Incomplete
    def __init__(self, system_template: str = '', user_template: str = '', separator: str = '\n', ignore_extra_keys: bool = False) -> None:
        '''Initializes a new instance of the AgnosticPromptBuilder class.

        Args:
            system_template (str, optional): The system prompt template. May contain placeholders enclosed in curly
                braces `{}`. Defaults to an empty string.
            user_template (str, optional): The user prompt template. May contain placeholders enclosed in curly
                braces `{}`. Defaults to an empty string.
            separator (str, optional): A string used to separate each prompt template\'s content. Defaults to "\\n".
            ignore_extra_keys (bool, optional): Whether to ignore extra keys when formatting the prompt.
                Defaults to False.
        '''
