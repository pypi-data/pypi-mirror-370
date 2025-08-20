from gllm_inference.prompt_formatter.prompt_formatter import BasePromptFormatter as BasePromptFormatter
from gllm_inference.schema import PromptRole as PromptRole

class OpenAIPromptFormatter(BasePromptFormatter):
    '''A prompt formatter that formats prompt with OpenAI\'s specific formatting.

    The `OpenAIPromptFormatter` class formats a prompt by utilizing OpenAI\'s specific formatting.

    Attributes:
        content_separator (str): A string used to separate each content in a message.

    Usage:
        The `OpenAIPromptFormatter` can be used to format a prompt for OpenAI\'s models.
        The `content_separator` can be customized to define the format of the prompt.

        Usage example:
        ```python
        prompt = [
            (PromptRole.USER, ["Hello", "how are you?"]),
            (PromptRole.ASSISTANT, ["I\'m fine", "thank you!"]),
            (PromptRole.USER, ["What is the capital of France?"]),
        ]
        prompt_formatter = OpenAIPromptFormatter(
            content_separator="---"
        )
        print(prompt_formatter.format(prompt))
        ```

        Output example:
        ```
        User: Hello---how are you?
        Assistant: I\'m fine---thank you!
        User: What is the capital of France?
        ```
    '''
