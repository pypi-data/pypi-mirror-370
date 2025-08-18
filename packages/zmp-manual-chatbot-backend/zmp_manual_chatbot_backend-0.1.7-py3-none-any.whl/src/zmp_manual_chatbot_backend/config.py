from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from dotenv import load_dotenv
import os
from typing import Dict, Any, Optional
from pydantic_settings import SettingsConfigDict

# Load environment variables from .env file if present
load_dotenv()

class Settings(BaseSettings):
    """
    Configuration management for the ZMP Manual Chatbot Backend.
    
    This class handles all application configuration using Pydantic BaseSettings
    with environment variable support. Configuration is loaded from:
    1. Environment variables
    2. .env file (if present)
    3. Default values defined in Field specifications
    
    The configuration supports multiple LLM providers (Ollama, OpenAI), OAuth2
    authentication with Keycloak, and various external service integrations.
    
    Example:
        # Create settings instance (automatically loads from environment)
        settings = Settings()
        
        # Access configuration values
        mcp_url = settings.MCP_SERVER_URL
        provider = settings.effective_llm_provider
        
    Streaming Configuration:
        CHAR_STREAMING_DELAY: Delay between characters in streaming (seconds)
        ENABLE_CHAR_STREAMING: Enable/disable character-level streaming
        
    Attributes:
        MCP_SERVER_URL: Base URL for the MCP (Model Context Protocol) Server
        LLM_PROVIDER: Primary LLM provider ('ollama', 'openai', 'huggingface')
        KEYCLOAK_SERVER_URL: Keycloak identity provider server URL
        ... (see individual field documentation below)
    """
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Domain Configuration
    DOMAIN: str = Field("localhost", description="Domain name")

    # MCP Server Configuration
    MCP_SERVER_URL: str = Field("http://localhost:5371/mcp", description="Base URL for the MCP Server")

    # General/Logging
    DEBUG: bool = Field(False, description="Enable debug mode")
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    ALLOWED_ORIGINS: str = Field("*", description="CORS allowed origins")
    ZMP_CLUSTER_MODE: bool = Field(False, description="Cluster mode enabled")

    # LLM Provider Configuration
    LLM_PROVIDER: str = Field("ollama", description="LLM provider: 'ollama', 'openai', or 'huggingface'")
    
    # OpenAI/LLM Configuration
    OPENAI_API_KEY: str = Field("", description="OpenAI API key")
    OPENAI_MODEL: str = Field("gpt-3.5-turbo", description="OpenAI model name")
    AGENT_LLM_MODEL: str = Field("", description="Agent LLM model name")
    IMAGE_ANALYSIS_MODEL: str = Field("", description="Image analysis model name")

    # Ollama Configuration
    OLLAMA_BASE_URL: str = Field("http://localhost:11434", description="Ollama server base URL")
    OLLAMA_MODEL: str = Field("llama3.2:3b", description="Ollama model name (recommended for 16GB M1 Mac)")
    OLLAMA_TEMPERATURE: float = Field(0.0, description="Ollama model temperature")
    OLLAMA_NUM_PREDICT: int = Field(2000, description="Ollama max tokens to generate")
    OLLAMA_TOP_K: int = Field(40, description="Ollama top-k sampling")
    OLLAMA_TOP_P: float = Field(0.9, description="Ollama top-p sampling")
    
    # Alternative Ollama models for different memory/performance needs:
    # For testing/minimal memory: "qwen2:1.5b" (~0.9GB)
    # For balanced performance: "phi3:mini" (~2.3GB) 
    # For best quality: "llama3.2:3b" (~2GB) - RECOMMENDED
    # For fastest responses: "llama3.2:1b" (~1.3GB)

    # Streaming Configuration
    ENABLE_CHAR_STREAMING: bool = Field(True, description="Enable character-level streaming for final_answer")
    CHAR_STREAMING_DELAY: float = Field(0.01, description="Delay between characters in streaming (seconds)")
    STREAMING_CHUNK_SIZE: int = Field(10, description="Number of characters per streaming chunk")

    # MongoDB Configuration
    MONGO_DB_URL: str = Field("", description="MongoDB connection URL")
    MONGO_DB_NAME: str = Field("", description="MongoDB database name")
    MONGO_DB_USER: str = Field("", description="MongoDB username")
    MONGO_DB_PASS: str = Field("", description="MongoDB password")
    MONGO_CHAT_COLLECTION_NAME: str = Field("", description="MongoDB chat collection name")

    # Redis Configuration
    REDIS_HOST: str = Field("localhost", description="Redis host")
    REDIS_PORT: int = Field(6379, description="Redis port")
    REDIS_DB: int = Field(0, description="Redis database index")
    REDIS_PASS: str = Field("", description="Redis password")

    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = Field("", description="AWS access key ID")
    AWS_SECRET_ACCESS_KEY: str = Field("", description="AWS secret access key")
    AWS_REGION: str = Field("", description="AWS region")
    S3_BUCKET_NAME: str = Field("", description="S3 bucket name")

    # Keycloak/OAuth2 Authentication Configuration
    KEYCLOAK_SERVER_URL: str = Field(
        "https://keycloak.ags.cloudzcp.net/auth", 
        description="Keycloak server URL (default for development)"
    )
    KEYCLOAK_REALM: str = Field("ags", description="Keycloak realm name")
    KEYCLOAK_CLIENT_ID: str = Field("zmp-client", description="Keycloak client ID")
    KEYCLOAK_CLIENT_SECRET: str = Field("", description="Keycloak client secret")
    KEYCLOAK_REDIRECT_URI: str = Field(
        "http://localhost:5370/auth/callback", 
        description="OAuth2 redirect URI for callback"
    )
    HTTP_CLIENT_SSL_VERIFY: bool = Field(True, description="HTTP client SSL verification")
    AUTH_ENABLED: bool = Field(True, description="Enable authentication requirement")

    # GitHub Token
    GITHUB_TOKEN: str = Field("", description="GitHub personal access token")

    @property
    def effective_llm_provider(self) -> str:
        """
        Determine the effective LLM provider with intelligent fallback logic.
        
        This property implements automatic provider detection and fallback:
        1. If 'ollama' is specified, checks if Ollama service is available
        2. Falls back to OpenAI if Ollama is unavailable and API key is present
        3. Returns the configured provider for other values
        
        Returns:
            str: The effective LLM provider name ('ollama' or 'openai')
            
        Raises:
            RuntimeError: If no valid LLM provider is available
            
        Example:
            provider = settings.effective_llm_provider
            if provider == "ollama":
                # Use Ollama client
            elif provider == "openai": 
                # Use OpenAI client
        """
        if self.LLM_PROVIDER == "ollama":
            if self._ollama_available():
                return "ollama"
            else:
                print("⚠️  Ollama provider selected but Ollama service is not available. Falling back to OpenAI.")
                return "openai"
        return self.LLM_PROVIDER

    @property
    def keycloak_auth_endpoint(self) -> str:
        """OAuth2 authorization endpoint URL."""
        return f"{self.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/auth"
    
    @property
    def keycloak_token_endpoint(self) -> str:
        """OAuth2 token endpoint URL."""
        return f"{self.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/token"
    
    @property
    def keycloak_userinfo_endpoint(self) -> str:
        """OAuth2 userinfo endpoint URL."""
        return f"{self.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
    
    @property
    def keycloak_jwks_endpoint(self) -> str:
        """OAuth2 JWKS (JSON Web Key Set) endpoint URL."""
        return f"{self.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{self.KEYCLOAK_REALM}/protocol/openid-connect/certs"
    
    @property
    def keycloak_configured(self) -> bool:
        """Check if Keycloak is properly configured."""
        return bool(
            self.KEYCLOAK_SERVER_URL and 
            self.KEYCLOAK_REALM and 
            self.KEYCLOAK_CLIENT_ID
        )
    
    def _ollama_available(self) -> bool:
        """
        Check if Ollama service is available by testing connectivity.
        
        This method attempts to connect to the Ollama service at the configured
        base URL and checks if it responds with a successful HTTP status.
        
        Returns:
            bool: True if Ollama service is available and responding, False otherwise
            
        Note:
            This method has a 2-second timeout to avoid blocking application startup
            if the Ollama service is not available.
        """
        try:
            import requests
            response = requests.get(f"{self.OLLAMA_BASE_URL}/api/tags", timeout=2)
            return response.status_code == 200
        except (requests.RequestException, ImportError, ConnectionError):
            return False

settings = Settings()


class ApplicationSettings(BaseSettings):
    """Settings for App."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="APP_", env_file=".env", extra="ignore"
    )
    name: str = "zmp-manual-chatbot"
    title: str = "ZMP Manual Chatbot"
    version: str | None = None
    description: str = "ZMP Manual Chatbot Backend Service Restful API"
    root_path: str = "/api/manual-chatbot/v1"
    docs_url: str = f"{root_path}/api-docs"
    redoc_url: str = f"{root_path}/api-redoc"
    openapi_url: str = f"{root_path}/openapi"


application_settings = ApplicationSettings()