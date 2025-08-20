from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from apolo_app_types import (
    AppInputs,
    AppOutputs,
)
from apolo_app_types.protocols.common import (
    IngressHttp,
    Preset,
    SchemaExtraMetadata,
    SchemaMetaType,
)
from apolo_app_types.protocols.common.networking import (
    HttpApi,
    RestAPI,
    ServiceAPI,
)
from apolo_app_types.protocols.common.openai_compat import (
    OpenAICompatChatAPI,
    OpenAICompatEmbeddingsAPI,
)
from apolo_app_types.protocols.common.secrets_ import OptionalStrOrSecret
from apolo_app_types.protocols.postgres import CrunchyPostgresUserCredentials


class LightRAGPersistence(BaseModel):
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="LightRAG Persistence",
            description="Configure persistent storage for LightRAG data and inputs.",
        ).as_json_schema_extra(),
    )

    rag_storage_size: int = Field(
        default=10,
        gt=0,
        json_schema_extra=SchemaExtraMetadata(
            title="RAG Storage Size (GB)",
            description="Size of the persistent volume for RAG data storage.",
        ).as_json_schema_extra(),
    )

    inputs_storage_size: int = Field(
        default=5,
        gt=0,
        json_schema_extra=SchemaExtraMetadata(
            title="Inputs Storage Size (GB)",
            description="Size of the persistent volume for input files.",
        ).as_json_schema_extra(),
    )

    @field_validator("rag_storage_size", "inputs_storage_size", mode="before")
    @classmethod
    def validate_storage_size(cls, value: int) -> int:
        if value and isinstance(value, int):
            if value < 1:
                error_message = "Storage size must be greater than 1GB."
                raise ValueError(error_message)
        else:
            error_message = "Storage size must be specified as int."
            raise ValueError(error_message)
        return value


# LLM Provider Types
class OpenAILLMProvider(RestAPI):
    """OpenAI LLM provider configuration. Also supports OpenRouter."""

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="OpenAI LLM Provider",
            description="OpenAI API configuration. Also supports OpenRouter.",
            meta_type=SchemaMetaType.INLINE,
        ).as_json_schema_extra(),
    )
    host: str = Field(default="api.openai.com", description="OpenAI API host")
    port: int = 443
    protocol: Literal["https"] = "https"
    timeout: int | None = Field(default=60, description="Connection timeout in seconds")
    base_path: str = "/v1"
    provider: Literal["openai"] = "openai"
    model: str = Field(default="gpt-4o-mini", description="Model name")
    api_key: OptionalStrOrSecret = Field(default=None, description="API key")


class AnthropicLLMProvider(RestAPI):
    """Anthropic Claude LLM provider configuration."""

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="Anthropic LLM Provider",
            description="Anthropic Claude API configuration.",
            meta_type=SchemaMetaType.INLINE,
        ).as_json_schema_extra(),
    )
    host: str = Field(default="api.anthropic.com", description="Anthropic API host")
    port: int = 443
    protocol: Literal["https"] = "https"
    timeout: int | None = Field(default=60, description="Connection timeout in seconds")
    base_path: str = "/v1"
    provider: Literal["anthropic"] = "anthropic"
    model: str = Field(
        default="claude-3-sonnet-20240229", description="Claude model name"
    )
    api_key: OptionalStrOrSecret = Field(default=None, description="Anthropic API key")


class OllamaLLMProvider(RestAPI):
    """Ollama local LLM provider configuration."""

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="Ollama LLM Provider",
            description="Ollama local model configuration.",
            meta_type=SchemaMetaType.INLINE,
        ).as_json_schema_extra(),
    )
    host: str = Field(description="Ollama server host")
    port: int = Field(default=11434, description="Ollama server port")
    protocol: Literal["http", "https"] = Field(
        default="http", description="Ollama server protocol"
    )
    timeout: int | None = Field(
        default=300, description="Connection timeout in seconds"
    )
    base_path: str = "/api"
    provider: Literal["ollama"] = "ollama"
    model: str = Field(default="llama3.1:8b", description="Ollama model name")


class GeminiLLMProvider(RestAPI):
    """Google Gemini LLM provider configuration."""

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="Google Gemini LLM Provider",
            description="Google Gemini API configuration.",
            meta_type=SchemaMetaType.INLINE,
        ).as_json_schema_extra(),
    )
    host: str = Field(
        default="generativelanguage.googleapis.com", description="Google AI API host"
    )
    port: int = 443
    protocol: Literal["https"] = "https"
    timeout: int | None = Field(default=60, description="Connection timeout in seconds")
    base_path: str = "/v1"
    provider: Literal["gemini"] = "gemini"
    model: str = Field(default="gemini-1.5-flash", description="Gemini model name")
    api_key: OptionalStrOrSecret = Field(default=None, description="Google AI API key")


# Union type for all LLM providers
LLMProvider = (
    OpenAICompatChatAPI
    | OpenAILLMProvider
    | AnthropicLLMProvider
    | OllamaLLMProvider
    | GeminiLLMProvider
)


# Embedding Provider Types
class OpenAIEmbeddingProvider(RestAPI):
    """OpenAI embedding provider configuration."""

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="OpenAI Embedding Provider",
            description="OpenAI embeddings API configuration.",
            meta_type=SchemaMetaType.INLINE,
        ).as_json_schema_extra(),
    )
    host: str = Field(default="api.openai.com", description="OpenAI API host")
    port: int = 443
    protocol: Literal["https"] = "https"
    timeout: int | None = Field(default=60, description="Connection timeout in seconds")
    base_path: str = "/v1"
    provider: Literal["openai"] = "openai"
    model: str = Field(
        default="text-embedding-ada-002", description="Embedding model name"
    )
    api_key: OptionalStrOrSecret = Field(default=None, description="OpenAI API key")


class OllamaEmbeddingProvider(RestAPI):
    """Ollama embedding provider configuration."""

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="Ollama Embedding Provider",
            description="Ollama local embedding model configuration.",
            meta_type=SchemaMetaType.INLINE,
        ).as_json_schema_extra(),
    )
    host: str = Field(description="Ollama server host")
    port: int = Field(default=11434, description="Ollama server port")
    protocol: Literal["http", "https"] = Field(
        default="http", description="Ollama server protocol"
    )
    timeout: int | None = Field(
        default=300, description="Connection timeout in seconds"
    )
    base_path: str = "/api"
    provider: Literal["ollama"] = "ollama"
    model: str = Field(
        default="nomic-embed-text", description="Ollama embedding model name"
    )


# Union type for all embedding providers
EmbeddingProvider = (
    OpenAICompatEmbeddingsAPI | OpenAIEmbeddingProvider | OllamaEmbeddingProvider
)


# For backward compatibility, create a simplified config
LightRAGLLMConfig = LLMProvider


# For backward compatibility, create a simplified config
LightRAGEmbeddingConfig = EmbeddingProvider


class LightRAGAppInputs(AppInputs):
    preset: Preset
    ingress_http: IngressHttp
    pgvector_user: CrunchyPostgresUserCredentials
    llm_config: LightRAGLLMConfig = Field(
        default=OpenAICompatChatAPI(host="", port=443, protocol="https"),
        description="LLM provider configuration",
    )
    embedding_config: LightRAGEmbeddingConfig = Field(
        default=OpenAICompatEmbeddingsAPI(host="", port=443, protocol="https"),
        description="Embedding provider configuration",
    )
    persistence: LightRAGPersistence = Field(default_factory=LightRAGPersistence)


class LightRAGAppOutputs(AppOutputs):
    """
    LightRAG outputs:
      - web_app_url: URL to access the web interface
      - server_url: URL to access the API server
    """

    web_app_url: ServiceAPI[HttpApi] | None = None
    server_url: ServiceAPI[HttpApi] | None = None
