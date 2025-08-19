import os
import warnings
from typing import Literal, Optional

from openai import OpenAI

from memory.configs.embeddings.base import BaseEmbedderConfig
from memory.embeddings.base import EmbeddingBase

class SoikaStackEmbedding(EmbeddingBase):
    def __init__(self, config: Optional[BaseEmbedderConfig] = None):
        super().__init__(config)

        self.config.model = self.config.model or "jina-embeddings-v2-base-en"

        api_key = self.config.api_key or os.getenv("SOIKASTACK_API_KEY")
        base_url = (
            self.config.soikastack_base_url
            or os.getenv("SOIKASTACK_API_BASE")
            or os.getenv("SOIKASTACK_BASE_URL")
            or "http://localhost:4141/v1"
        )
        if os.environ.get("SOIKASTACK_API_BASE"):
            warnings.warn(
                "The environment variable 'SOIKASTACK_API_BASE' is deprecated and will be removed in the 0.1.80. "
                "Please use 'SOIKASTACK_BASE_URL' instead.",
                DeprecationWarning,
            )

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def embed(self, text, memory_action: Optional[Literal["add", "search", "update"]] = None):
        """
        Get the embedding for the given text using OpenAI.

        Args:
            text (str): The text to embed.
            memory_action (optional): The type of embedding to use. Must be one of "add", "search", or "update". Defaults to None.
        Returns:
            list: The embedding vector.
        """
        text = text.replace("\n", " ")
        return (
            self.client.embeddings.create(input=[text], model=self.config.model)
            .data[0]
            .embedding
        )