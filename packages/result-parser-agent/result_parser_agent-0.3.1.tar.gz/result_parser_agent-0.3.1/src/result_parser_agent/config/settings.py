"""Configuration management for the results parser agent."""

from pydantic.v1 import BaseSettings, Field, SecretStr, validator


class ParserConfig(BaseSettings):
    """Unified configuration class for the results parser agent."""

    # LLM Configuration
    LLM_PROVIDER: str = Field(
        default="openai",
        description="LLM provider (groq, openai, anthropic, ollama, google)",
    )
    LLM_MODEL: str = Field(default="gpt-4o", description="LLM model to use")
    LLM_MAX_TOKENS: int = Field(
        default=4000, description="Maximum tokens for responses"
    )

    # API Keys (following your existing pattern)
    # GROQ_API_KEY: SecretStr = Field(..., description="Groq API key")
    OPENAI_API_KEY: SecretStr = Field(..., description="OpenAI API key")
    # GOOGLE_API_KEY: SecretStr = Field(..., description="Google API key")

    # Agent Configuration
    AGENT_MAX_RETRIES: int = Field(default=3, description="Maximum number of retries")
    AGENT_CHUNK_SIZE: int = Field(
        default=2000, description="Size of file chunks to process"
    )
    AGENT_TIMEOUT: int = Field(
        default=300, description="Timeout for operations in seconds"
    )
    AGENT_DEBUG: bool = Field(default=False, description="Enable debug mode")

    # Output Configuration
    OUTPUT_PRETTY_PRINT: bool = Field(
        default=True, description="Pretty print JSON output"
    )

    # Environment variable settings
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @validator("OPENAI_API_KEY")
    def validate_openai_api_key(cls, v: SecretStr):
        """Validate OpenAI API key format (following your existing pattern)."""
        secret = v.get_secret_value()
        if not secret.startswith("sk-"):
            raise ValueError("Invalid OpenAI API key format")
        return v


settings = ParserConfig()
