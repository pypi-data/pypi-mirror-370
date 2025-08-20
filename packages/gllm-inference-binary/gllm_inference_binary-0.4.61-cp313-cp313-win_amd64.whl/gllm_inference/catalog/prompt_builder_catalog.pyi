from _typeshed import Incomplete
from gllm_inference.catalog.catalog import BaseCatalog as BaseCatalog, logger as logger
from gllm_inference.catalog.component_map import PROMPT_BUILDER_TYPE_MAP as PROMPT_BUILDER_TYPE_MAP
from gllm_inference.multimodal_prompt_builder import MultimodalPromptBuilder as MultimodalPromptBuilder
from gllm_inference.prompt_builder.prompt_builder import BasePromptBuilder as BasePromptBuilder, PromptBuilder as PromptBuilder

PROMPT_BUILDER_MODEL_PARAM_MAP: Incomplete
PROMPT_BUILDER_REQUIRED_COLUMNS: Incomplete

class PromptBuilderCatalog(BaseCatalog[BasePromptBuilder | MultimodalPromptBuilder | PromptBuilder]):
    '''Loads multiple prompt builders from certain sources.

    Attributes:
        components (dict[str, BasePromptBuilder | MultimodalPromptBuilder | PromptBuilder]):
            Dictionary of the loaded prompt builders.

    Initialization:
        # Example 1: Load from Google Sheets using client email and private key
        ```python
        catalog = PromptBuilderCatalog.from_gsheets(
            sheet_id="...",
            worksheet_id="...",
            client_email="...",
            private_key="...",
        )

        prompt_builder = catalog.name
        ```

        # Example 2: Load from Google Sheets using credential file
        ```python
        catalog = PromptBuilderCatalog.from_gsheets(
            sheet_id="...",
            worksheet_id="...",
            credential_file_path="...",
        )

        prompt_builder = catalog.name
        ```

        # Example 3: Load from CSV
        ```python
        catalog = PromptBuilderCatalog.from_csv(csv_path="...")

        prompt_builder = catalog.name
        ```

        # Example 4: Load from records
        ```python
        catalog = PromptBuilderCatalog.from_records(
            records=[
                {
                    "name": "summarize",
                    "system": "You are an AI expert\\nSummarize the following context.\\n\\nContext:\\n```{context}```",
                    "user": ""
                },
                {
                    "name": "transform_query",
                    "system": "",
                    "user": "Transform the following query into a simpler form.\\n\\nQuery:\\n```{query}```"
                },
                {
                    "name": "draft_document",
                    "system": (
                        "You are an AI expert.\\nDraft a document following the provided format and context.\\n\\n"
                        "Format:\\n```{format}```\\n\\nContext:\\n```{context}```"
                    ),
                    "user": "User instruction:\\n{query}"
                },
            ]
        )

        prompt_builder = catalog.answer_question
        ```

    Template Example:
        # Example 1: Google Sheets
        For an example of how a Google Sheets file can be formatted to be loaded using PromptBuilderCatalog, see:
        https://docs.google.com/spreadsheets/d/12IwSKv8hMhyWXSQnLx9LgCj0cxaR1f9gOmbEDGleurE/edit?usp=drive_link

        # Example 2: CSV
        For an example of how a CSV file can be formatted to be loaded using PromptBuilderCatalog, see:
        https://drive.google.com/file/d/1CWijOk-g16ZglUn_K2bDPmbyyBDK2r0L/view?usp=drive_link


    Template explanation:
        The required columns are:
            1. name (str): The name of the prompt builder.
            2. system (str): The system template of the prompt builder.
            3. user (str): The user template of the prompt builder.

        Important Notes:
            1. At least one of the `system` and `user` columns must be filled.

    WARNING: The use of BasePromptBuilder | MultimodalPromptBuilder is deprecated and will be removed in version 0.5.0.
    Please use PromptBuilder instead.
    '''
