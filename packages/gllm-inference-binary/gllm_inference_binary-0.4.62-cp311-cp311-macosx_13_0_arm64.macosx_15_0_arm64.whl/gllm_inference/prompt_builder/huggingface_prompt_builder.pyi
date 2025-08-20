from _typeshed import Incomplete
from gllm_inference.prompt_builder.prompt_builder import BasePromptBuilder as BasePromptBuilder
from gllm_inference.prompt_formatter import HuggingFacePromptFormatter as HuggingFacePromptFormatter
from gllm_inference.schema import PromptRole as PromptRole

DEPRECATION_MESSAGE: str

class HuggingFacePromptBuilder(BasePromptBuilder):
    """A prompt builder for Hugging Face models that support chat templating.

    The `HuggingFacePromptBuilder` class is designed to create prompts compatible with models hosted in Hugging Face,
    given that the model support chat templating. It loads the appropriate tokenizer and formats the prompt by
    injecting placeholder values.

    Attributes:
        system_template (str): The system prompt template. May contain placeholders enclosed in curly braces `{}`.
        user_template (str): The user prompt template. May contain placeholders enclosed in curly braces `{}`.
        prompt_key_set (set[str]): A set of expected keys that must be present in the prompt templates.
        ignore_extra_keys (bool): Whether to ignore extra keys when formatting the prompt.
        formatter (HuggingFacePromptFormatter): The formatter to be used to format the prompt into a string in the
            `format_as_string` method.

    Note:
        If you're trying to access the prompt builder template of a gated model, you'd need to:
        1. Request access to the gated repo using your HuggingFace account.
        2. Login to HuggingFace in your system. This can be done as follows:
           2.1. Install huggingface-hub: ```pip install huggingface-hub```
           2.2. Login to HuggingFace: ```huggingface-cli login```
           2.3. Enter your HuggingFace token.
    """
    formatter: Incomplete
    def __init__(self, system_template: str = '', user_template: str = '', model_name_or_path: str = '', ignore_extra_keys: bool = False) -> None:
        """Initializes a new instance of the HuggingFacePromptBuilder class.

        Args:
            system_template (str, optional): The system prompt template. May contain placeholders enclosed in curly
                braces `{}`. Defaults to an empty string.
            user_template (str, optional): The user prompt template. May contain placeholders enclosed in curly
                braces `{}`. Defaults to an empty string.
            model_name_or_path (str, optional): The model name or path of the Hugging Face model tokenizer to be loaded.
                Defaults to an empty string.
            ignore_extra_keys (bool, optional): Whether to ignore extra keys when formatting the prompt.
                Defaults to False.
        """
