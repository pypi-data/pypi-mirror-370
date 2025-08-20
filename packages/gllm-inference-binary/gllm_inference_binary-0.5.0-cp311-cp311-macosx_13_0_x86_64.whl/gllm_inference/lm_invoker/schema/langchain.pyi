class Key:
    """Defines valid keys in LangChain."""
    ARGS: str
    FINISH_REASON: str
    ID: str
    IMAGE_URL: str
    INPUT_TOKENS: str
    NAME: str
    OUTPUT_TOKENS: str
    PARSED: str
    RAW: str
    TEXT: str
    TYPE: str
    URL: str

class InputType:
    """Defines valid input types in LangChain."""
    IMAGE_URL: str
    TEXT: str
    TOOL_CALL: str
