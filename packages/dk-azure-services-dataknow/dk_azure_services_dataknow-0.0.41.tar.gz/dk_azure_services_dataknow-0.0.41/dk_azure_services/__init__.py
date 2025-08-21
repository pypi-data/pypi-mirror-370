"""
DK Azure Services Package
Paquete para facilitar la integración con servicios de Azure.

Incluye conectores asíncronos optimizados para:
- Azure Cosmos DB
- Azure OpenAI (próximamente)
- Azure Blob Storage (próximamente)  
- Azure Key Vault
"""

__version__ = "0.0.41"
__author__ = "Leonar Santiago Castro"

# API limpia - Solo versiones asíncronas (renombradas sin prefijo)
from .cosmos import AsyncCosmosDBClient as CosmosDBClient
from .common.auth import AsyncAzureAuthenticator as AzureAuthenticator
from .common.config import AsyncConfigManager as ConfigManager
from .datalake.async_datalake import AsyncDataLake
from .blob_storage.async_blob_storage import AsyncBlobStorage
from .searchai.async_search import AsyncSearchEngine

__all__ = [
    "CosmosDBClient",
    "AzureAuthenticator", 
    "ConfigManager",
    "AsyncDataLake",
    "AsyncBlobStorage",
    "AsyncSearchEngine"
] 