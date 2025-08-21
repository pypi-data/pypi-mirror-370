"""
Módulo común con utilidades asíncronas compartidas para todos los servicios de Azure.

Proporciona infraestructura base compartida incluyendo:
- Gestión centralizada de configuración con soporte para Key Vault
- Autenticación unificada para todos los servicios de Azure
- Manejo estructurado de errores específicos por servicio
- Configuración avanzada de logging para aplicaciones de producción

Componentes principales:
    - AsyncConfigManager: Gestión de configuración y secretos (RECOMENDADO)
    - AsyncAzureAuthenticator: Autenticación centralizada
    - Sistema de excepciones: Manejo de errores específico por servicio

Ejemplo de uso básico:
    >>> from dk_azure_services.common import AsyncConfigManager
    >>> 
    >>> async with AsyncConfigManager() as config:
    ...     # Jerarquía automática: env var → Key Vault → default
    ...     cosmos_uri = await config.get_config_value("COSMOS_URI")
    ...     
    ...     # Configuración completa por servicio
    ...     cosmos_config = await config.get_cosmos_config()
    ...     
    ...     # Secretos específicos de Key Vault
    ...     api_secret = await config.get_secret_from_key_vault("external-api-key")

Para autenticación:
    >>> from dk_azure_services.common import AsyncAzureAuthenticator
    >>> 
    >>> # Singleton - una instancia para toda la aplicación
    >>> auth = AsyncAzureAuthenticator()
    >>> credential = await auth.get_credential()
    >>> 
    >>> # Verificar autenticación
    >>> if await auth.test_authentication():
    ...     print("✅ Autenticado con Azure")

Para manejo de errores:
    >>> from dk_azure_services.common import ConfigurationError, KeyVaultError
    >>> 
    >>> try:
    ...     secret = await config.get_secret_from_key_vault("missing-secret")
    >>> except KeyVaultError as e:
    ...     print(f"Secreto no encontrado: {e.secret_name}")
    >>> except ConfigurationError as e:
    ...     print(f"Configuración faltante: {e.missing_config}")
"""

from .auth import AsyncAzureAuthenticator
from .config import AsyncConfigManager
from .exceptions import (
    AzureServiceError,
    ConfigurationError,
    AuthenticationError,
    CosmosDBError,
    OpenAIError,
    BlobStorageError,
    KeyVaultError
)

__all__ = [
    # 🔑 Gestión de Configuración y Secretos (PRINCIPAL)
    "AsyncConfigManager",        # Configuración centralizada + Key Vault
    
    # 🔐 Autenticación Centralizada
    "AsyncAzureAuthenticator",   # Autenticación singleton para Azure
    
    # ⚠️ Sistema de Excepciones Estructurado
    "AzureServiceError",         # Clase base para errores de Azure
    "ConfigurationError",        # Errores de configuración faltante
    "AuthenticationError",       # Errores de autenticación
    "KeyVaultError",            # Errores específicos de Key Vault
    "CosmosDBError",            # Errores específicos de Cosmos DB
    "OpenAIError",              # Errores específicos de OpenAI
    "BlobStorageError"          # Errores específicos de Blob Storage
]

# Información del módulo
__version__ = "1.0.0"
__author__ = "DK Azure Services Team"
__description__ = "Infraestructura compartida para servicios de Azure con Key Vault y autenticación centralizada" 