"""Azure service configuration and credential management."""
import os
from azure.identity import (
    DefaultAzureCredential,
    ManagedIdentityCredential,
    ClientSecretCredential
)
from azure.keyvault.secrets import SecretClient
from typing import Optional
from .settings import settings


class AzureConfig:
    """Azure service configuration and credential management."""
    
    def __init__(self):
        self._credential = None
        self._key_vault_client = None
    
    @property
    def credential(self):
        """Get Azure credential (Managed Identity or Service Principal)."""
        if self._credential is None:
            # Try Managed Identity first (for production)
            if os.getenv("WEBSITE_INSTANCE_ID"):
                self._credential = ManagedIdentityCredential()
            elif settings.azure_client_id and settings.azure_client_secret:
                # Use Service Principal (for development)
                self._credential = ClientSecretCredential(
                    tenant_id=settings.azure_tenant_id,
                    client_id=settings.azure_client_id,
                    client_secret=settings.azure_client_secret
                )
            else:
                # Use DefaultAzureCredential (tries multiple methods)
                self._credential = DefaultAzureCredential()
        return self._credential
    
    @property
    def key_vault_client(self) -> Optional[SecretClient]:
        """Get Azure Key Vault client."""
        if not settings.azure_key_vault_name:
            return None
            
        if self._key_vault_client is None:
            vault_url = f"https://{settings.azure_key_vault_name}.vault.azure.net/"
            self._key_vault_client = SecretClient(
                vault_url=vault_url,
                credential=self.credential
            )
        return self._key_vault_client
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        """Get secret from Key Vault."""
        if not self.key_vault_client:
            return None
        try:
            secret = self.key_vault_client.get_secret(secret_name)
            return secret.value
        except Exception:
            return None


# Global Azure config instance
azure_config = AzureConfig()

