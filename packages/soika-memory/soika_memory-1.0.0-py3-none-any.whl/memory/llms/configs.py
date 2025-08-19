from typing import Optional

from pydantic import BaseModel, Field, field_validator


class LlmConfig(BaseModel):
    provider: str = Field(description="Provider of the LLM (e.g., 'soikastack', 'openai')", default="soikastack")
    config: Optional[dict] = Field(description="Configuration for the specific LLM", default={})

    @field_validator("config")
    def validate_config(cls, v, values):
        provider = values.data.get("provider")
        if provider in (
            "soikastack",
            "openai",
            "ollama",
            "anthropic",
            "groq",
            "together",
            "aws_bedrock",
            "azure_openai",
            "openai_structured",
            "azure_openai_structured",
            "gemini",
            "deepseek",
            "xai",
        ):
            return v
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
