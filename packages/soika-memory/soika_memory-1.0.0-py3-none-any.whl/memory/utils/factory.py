import importlib
from typing import Optional

from memory.configs.embeddings.base import BaseEmbedderConfig
from memory.configs.llms.base import BaseLlmConfig
from memory.embeddings.mock import MockEmbeddings


def load_class(class_type):
    module_path, class_name = class_type.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class LlmFactory:
    provider_to_class = {
        "soikastack": "memory.llms.soikastack.SoikaStackLLM",
        "ollama": "memory.llms.ollama.OllamaLLM",
        "openai": "memory.llms.openai.OpenAILLM",
        "groq": "memory.llms.groq.GroqLLM",
        "together": "memory.llms.together.TogetherLLM",
        "aws_bedrock": "memory.llms.aws_bedrock.AWSBedrockLLM",
        "azure_openai": "memory.llms.azure_openai.AzureOpenAILLM",
        "openai_structured": "memory.llms.openai_structured.OpenAIStructuredLLM",
        "anthropic": "memory.llms.anthropic.AnthropicLLM",
        "azure_openai_structured": "memory.llms.azure_openai_structured.AzureOpenAIStructuredLLM",
        "gemini": "memory.llms.gemini.GeminiLLM",
        "deepseek": "memory.llms.deepseek.DeepSeekLLM",
        "xai": "memory.llms.xai.XAILLM",
    }

    @classmethod
    def create(cls, provider_name, config):
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            llm_instance = load_class(class_type)
            base_config = BaseLlmConfig(**config)
            return llm_instance(base_config)
        else:
            raise ValueError(f"Unsupported Llm provider: {provider_name}")


class EmbedderFactory:
    provider_to_class = {
        "soikastack": "memory.embeddings.soikastack.SoikaStackEmbedding",
        "openai": "memory.embeddings.openai.OpenAIEmbedding",
        "ollama": "memory.embeddings.ollama.OllamaEmbedding",
        "huggingface": "memory.embeddings.huggingface.HuggingFaceEmbedding",
        "azure_openai": "memory.embeddings.azure_openai.AzureOpenAIEmbedding",
        "gemini": "memory.embeddings.gemini.GoogleGenAIEmbedding",
        "vertexai": "memory.embeddings.vertexai.VertexAIEmbedding",
        "together": "memory.embeddings.together.TogetherEmbedding",
        "lmstudio": "memory.embeddings.lmstudio.LMStudioEmbedding",
        "langchain": "memory.embeddings.langchain.LangchainEmbedding",
        "aws_bedrock": "memory.embeddings.aws_bedrock.AWSBedrockEmbedding",
    }

    @classmethod
    def create(cls, provider_name, config, vector_config: Optional[dict]):
        if provider_name == "upstash_vector" and vector_config and vector_config.enable_embeddings:
            return MockEmbeddings()
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            embedder_instance = load_class(class_type)
            base_config = BaseEmbedderConfig(**config)
            return embedder_instance(base_config)
        else:
            raise ValueError(f"Unsupported Embedder provider: {provider_name}")


class VectorStoreFactory:
    provider_to_class = {
        "qdrant": "memory.vector_stores.qdrant.Qdrant",
        "chroma": "memory.vector_stores.chroma.ChromaDB",
        "pgvector": "memory.vector_stores.pgvector.PGVector",
        "milvus": "memory.vector_stores.milvus.MilvusDB",
        "upstash_vector": "memory.vector_stores.upstash_vector.UpstashVector",
        "azure_ai_search": "memory.vector_stores.azure_ai_search.AzureAISearch",
        "pinecone": "memory.vector_stores.pinecone.PineconeDB",
        "mongodb": "memory.vector_stores.mongodb.MongoDB",
        "redis": "memory.vector_stores.redis.RedisDB",
        "elasticsearch": "memory.vector_stores.elasticsearch.ElasticsearchDB",
        "vertex_ai_vector_search": "memory.vector_stores.vertex_ai_vector_search.GoogleMatchingEngine",
        "opensearch": "memory.vector_stores.opensearch.OpenSearchDB",
        "supabase": "memory.vector_stores.supabase.Supabase",
        "weaviate": "memory.vector_stores.weaviate.Weaviate",
        "faiss": "memory.vector_stores.faiss.FAISS",
        "langchain": "memory.vector_stores.langchain.Langchain",
    }

    @classmethod
    def create(cls, provider_name, config):
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            if not isinstance(config, dict):
                config = config.model_dump()
            vector_store_instance = load_class(class_type)
            return vector_store_instance(**config)
        else:
            raise ValueError(f"Unsupported VectorStore provider: {provider_name}")

    @classmethod
    def reset(cls, instance):
        instance.reset()
        return instance
