"""Application settings management."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure Configuration
    azure_subscription_id: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_resource_group: str = "rg-databricks-ai-agent"
    
    # Azure OpenAI
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment_name: str = "gpt-4o"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    
    # Azure AI Search
    azure_search_endpoint: Optional[str] = None
    azure_search_api_key: Optional[str] = None
    azure_search_index_name: str = "recommendations-index"
    
    # Database Configuration
    # PostgreSQL (preferred for local development)
    postgres_host: Optional[str] = None
    postgres_port: int = 5432
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_database: Optional[str] = None
    postgres_ssl_mode: str = "prefer"  # disable, allow, prefer, require, verify-ca, verify-full
    
    # Azure SQL Database (legacy/alternative)
    azure_sql_server: Optional[str] = None
    azure_sql_database: Optional[str] = None
    azure_sql_username: Optional[str] = None
    azure_sql_password: Optional[str] = None
    
    # Database selection
    use_postgres: bool = True  # Set to False to use SQL Server
    
    # Azure Blob Storage
    azure_storage_account: Optional[str] = None
    azure_storage_key: Optional[str] = None
    azure_storage_container: str = "ai-agent-data"
    
    # Azure Key Vault
    azure_key_vault_name: Optional[str] = None
    
    # Databricks
    databricks_server_hostname: Optional[str] = None
    databricks_http_path: Optional[str] = None
    databricks_token: Optional[str] = None
    
    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    use_local_data: bool = False  # Set to True to use CSV data instead of Databricks
    local_data_path: Optional[str] = None  # Path to CSV file, defaults to data/sample_job_metrics.csv
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
# Initialize settings, handling missing or unreadable .env file gracefully
import warnings
import os

# Temporarily disable .env file loading if there are permission issues
env_file_backup = None
if os.path.exists(".env"):
    try:
        # Test if we can read the file
        with open(".env", "r"):
            pass
    except (PermissionError, IOError):
        # Can't read .env, temporarily rename the Config's env_file
        env_file_backup = Settings.Config.env_file
        Settings.Config.env_file = None

try:
    settings = Settings()
    if env_file_backup is not None:
        # Restore the original env_file setting
        Settings.Config.env_file = env_file_backup
        warnings.warn("Could not read .env file due to permissions. Using environment variables only.")
except Exception as e:
    # Fallback: create settings without .env file
    if env_file_backup is not None:
        Settings.Config.env_file = env_file_backup
    warnings.warn(f"Error loading settings: {e}. Using defaults.")
    # Create minimal settings
    settings = Settings(_env_file=None)

