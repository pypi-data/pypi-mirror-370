from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    """
    ModelInfo is a Pydantic model that contains information about a model's properties.

    This replaces the TypedDict from autogen_core.models.ModelInfo to provide better
    type safety and validation.
    """

    vision: bool = Field(
        default=False,
        description="True if the model supports vision, aka image input, otherwise False.",
    )

    function_calling: bool = Field(
        default=True,
        description="True if the model supports function calling, otherwise False.",
    )

    json_output: bool = Field(
        default=True,
        description="True if the model supports json output, otherwise False. Note: this is different to structured json.",
    )

    family: str = Field(
        default="UNKNOWN",
        description="Model family should be one of the constants from ModelFamily or a string representing an unknown model family.",
    )

    structured_output: bool = Field(
        default=True,
        description="True if the model supports structured output, otherwise False. This is different to json_output.",
    )

    multiple_system_messages: bool | None = Field(
        default=False,
        description="True if the model supports multiple, non-consecutive system messages, otherwise False.",
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "vision": True,
                    "function_calling": True,
                    "json_output": True,
                    "family": "gpt-4o",
                    "structured_output": True,
                    "multiple_system_messages": True,
                }
            ]
        },
    }
