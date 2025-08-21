"""
Módulo de configuración centralizada para servicios de Azure.
"""

import os
import asyncio
import logging
import warnings
from typing import Dict, Optional, Any, Union
from azure.keyvault.secrets import SecretClient
from azure.keyvault.secrets.aio import SecretClient as AsyncSecretClient
from azure.identity.aio import DefaultAzureCredential
from .auth import AzureAuthenticator, AsyncAzureAuthenticator
from .exceptions import ConfigurationError, KeyVaultError

logger = logging.getLogger(__name__)


def configure_azure_logging(level: int = logging.WARNING):
    """
    Configura el nivel de logging para los servicios de Azure.
    
    Args:
        level: Nivel de logging deseado (logging.DEBUG, logging.INFO, etc.)
    """
    azure_loggers = [
        'azure',
        'azure.core',
        'azure.cosmos', 
        'azure.keyvault',
        'azure.identity',
        'azure.storage',
        'uamqp',
        'urllib3'
    ]
    
    for logger_name in azure_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    # Silenciar warnings específicos de asyncio sobre conexiones no cerradas
    # que son comunes con Azure SDK
    _silence_asyncio_unclosed_warnings()


def _silence_asyncio_unclosed_warnings():
    """
    Silencia los warnings de asyncio sobre client sessions no cerradas.
    
    Estos warnings son comunes con Azure SDK y no indican un problema real
    en la mayoría de los casos.
    """
    warnings.filterwarnings(
        "ignore",
        category=ResourceWarning,
        message="unclosed.*client_session"
    )
    
    warnings.filterwarnings(
        "ignore", 
        category=ResourceWarning,
        message="unclosed.*ssl.SSLSocket"
    )
    
    # Configurar el logger de asyncio para ser menos verboso
    asyncio_logger = logging.getLogger('asyncio')
    asyncio_logger.setLevel(logging.CRITICAL)


def setup_application_logging(
    level: int = logging.INFO,
    format_string: str = None,
    reduce_azure_logs: bool = True
):
    """
    Configura el logging para la aplicación completa.
    
    Args:
        level: Nivel de logging para la aplicación
        format_string: Formato personalizado para los logs
        reduce_azure_logs: Si se debe reducir la verbosidad de Azure SDK
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configurar logging básico
    logging.basicConfig(
        level=level,
        format=format_string,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Reducir logs de Azure si se solicita
    if reduce_azure_logs:
        configure_azure_logging(logging.WARNING)
    else:
        configure_azure_logging(logging.INFO)
    
    # Siempre silenciar warnings de conexiones no cerradas
    _silence_asyncio_unclosed_warnings()


class ConfigManager:
    """
    Administrador centralizado de configuración para todos los servicios de Azure.
    
    Maneja la carga de configuración desde variables de entorno y Azure Key Vault,
    proporcionando un punto único de acceso a la configuración de la aplicación.
    """
    
    def __init__(self, environment: str = None, key_vault_name: str = None):
        """
        Inicializa el administrador de configuración.
        
        Args:
            environment (str, optional): Entorno actual (dev, prod, etc.). 
                                       Si no se proporciona, se obtiene de APP_ENV
            key_vault_name (str, optional): Nombre del Key Vault. 
                                           Si no se proporciona, se obtiene de KEY_VAULT_NAME
        """
        self.environment = environment or os.getenv("APP_ENV", "dev")
        self.key_vault_name = key_vault_name or os.getenv("KEY_VAULT_NAME")
        self._key_vault_client = None
        self._config_cache = {}
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        
    def _get_key_vault_client(self) -> SecretClient:
        """
        Obtiene o inicializa el cliente de Key Vault.
        
        Returns:
            SecretClient: Cliente configurado para Key Vault
            
        Raises:
            ConfigurationError: Si no se puede acceder al Key Vault
        """
        if self._key_vault_client is None:
            if not self.key_vault_name:
                raise ConfigurationError(
                    "Nombre del Key Vault no configurado",
                    missing_config="KEY_VAULT_NAME"
                )
            
            try:
                authenticator = AzureAuthenticator()
                vault_url = f"https://{self.key_vault_name}.vault.azure.net"
                self._key_vault_client = SecretClient(
                    vault_url=vault_url,
                    credential=authenticator.get_credential()
                )
                logger.info(f"Cliente de Key Vault inicializado: {vault_url}")
            except Exception as e:
                raise ConfigurationError(f"Error al inicializar Key Vault: {e}")
                
        return self._key_vault_client
    
    def get_secret_from_key_vault(self, secret_name: str) -> str:
        """
        Obtiene un secreto desde Azure Key Vault.
        
        Args:
            secret_name (str): Nombre del secreto a recuperar
            
        Returns:
            str: Valor del secreto
            
        Raises:
            KeyVaultError: Si no se puede obtener el secreto
        """
        try:
            client = self._get_key_vault_client()
            secret = client.get_secret(secret_name)
            logger.info(f"Secreto '{secret_name}' obtenido exitosamente")
            return secret.value
        except Exception as e:
            logger.error(f"Error al obtener secreto '{secret_name}': {e}")
            raise KeyVaultError(
                f"No se pudo obtener el secreto '{secret_name}': {e}",
                secret_name=secret_name
            )
    
    def get_config_value(self, key: str, required: bool = True, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración desde variables de entorno o Key Vault.
        
        La búsqueda se realiza en el siguiente orden:
        1. Variables de entorno (ej: COSMOS_URI)
        2. Key Vault del entorno actual (ej: cosmos-uri)
        3. Valor por defecto si se proporciona
        
        Args:
            key (str): Clave de configuración a buscar
            required (bool): Si es requerido el valor
            default (Any): Valor por defecto si no se encuentra
            
        Returns:
            Any: Valor de configuración encontrado
            
        Raises:
            ConfigurationError: Si el valor es requerido y no se encuentra
        """
        # Verificar caché primero
        cache_key = f"{self.environment}:{key}"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        # 1. Variable de entorno (estándar, sin prefijo de ambiente)
        env_key = key.upper()
        value = os.getenv(env_key)
        
        if value:
            logger.debug(f"Configuración encontrada en variable de entorno: {env_key}")
            self._config_cache[cache_key] = value
            return value
        
        # 2. Key Vault (sin prefijo de ambiente, el ambiente se maneja por Key Vault diferente)
        secret_name = key.lower().replace('_', '-')
        try:
            value = self.get_secret_from_key_vault(secret_name)
            if value:
                logger.debug(f"Configuración encontrada en Key Vault: {secret_name}")
                self._config_cache[cache_key] = value
                return value
        except KeyVaultError:
            logger.debug(f"No se encontró secreto en Key Vault: {secret_name}")
        
        # 3. Valor por defecto
        if default is not None:
            logger.debug(f"Usando valor por defecto para {key}: {default}")
            self._config_cache[cache_key] = default
            return default
        
        # Si es requerido y no se encontró, lanzar error
        if required:
            raise ConfigurationError(
                f"Configuración requerida no encontrada: {key}. "
                f"Asegúrate de configurar la variable {env_key} o el secreto {secret_name} en Key Vault.",
                missing_config=key
            )
        
        return None
    
    def get_cosmos_config(self) -> Dict[str, str]:
        """
        Obtiene la configuración específica para Azure Cosmos DB.
        
        Returns:
            Dict[str, str]: Diccionario con configuración de Cosmos DB
        """
        return {
            "uri": self.get_config_value("COSMOS_URI"),
            "key": self.get_config_value("COSMOS_KEY"),
            "database_name": self.get_config_value("COSMOS_DATABASE"),
            "container_name": self.get_config_value("COSMOS_CONTAINER"),
            "partition_key": self.get_config_value("COSMOS_PARTITION", required=False, default="/id")
        }
    
    def get_openai_config(self) -> Dict[str, str]:
        """
        Obtiene la configuración específica para Azure OpenAI.
        
        Returns:
            Dict[str, str]: Diccionario con configuración de OpenAI
        """
        return {
            "endpoint": self.get_config_value("OPENAI_ENDPOINT"),
            "api_key": self.get_config_value("OPENAI_API_KEY"),
            "api_version": self.get_config_value("OPENAI_API_VERSION", required=False, default="2024-02-01"),
            "deployment_name": self.get_config_value("OPENAI_DEPLOYMENT_NAME")
        }
    
    def get_storage_config(self) -> Dict[str, str]:
        """
        Obtiene la configuración específica para Azure Blob Storage.
        
        Returns:
            Dict[str, str]: Diccionario con configuración de Blob Storage
        """
        return {
            "account_name": self.get_config_value("STORAGE_ACCOUNT_NAME"),
            "account_key": self.get_config_value("STORAGE_ACCOUNT_KEY", required=False),
            "connection_string": self.get_config_value("STORAGE_CONNECTION_STRING", required=False),
            "container_name": self.get_config_value("STORAGE_CONTAINER", required=False, default="documents")
        }
    
    def clear_cache(self):
        """
        Limpia la caché de configuración.
        """
        self._config_cache.clear()
        logger.info("Caché de configuración limpiada")
    
    def set_environment(self, environment: str):
        """
        Cambia el entorno actual y limpia la caché.
        
        Args:
            environment (str): Nuevo entorno a configurar
        """
        self.environment = environment
        self.clear_cache()
        logger.info(f"Entorno cambiado a: {environment}") 
        
    # Configuración Recurso Datalake
    def get_datalake_config(self) -> dict:
        """
        Devuelve la configuración de Azure Data Lake (síncrona).
        """
        return {
            "account_name": self.get_secret("datalake-account-name"),
            "file_system_name": self.get_secret("datalake-file-system-name"),
            "account_key": self.get_secret("datalake-account-key")
        }
         # Configuración Recurso Azure Search (síncrono)
    def get_search_config(self) -> dict:
        return {
            "endpoint": self.get_config_value("SEARCH_ENDPOINT"),
            "index_name": self.get_config_value("SEARCH_INDEX_NAME"),
            "api_key": self.get_config_value("SEARCH_API_KEY")
        }


class AsyncConfigManager:
    """
    Administrador centralizado de configuración asíncrono para todos los servicios de Azure.
    
    Versión asíncrona que proporciona la misma funcionalidad pero optimizada para
    operaciones concurrentes y de alto rendimiento.
    """
    
    def __init__(self, environment: str = None, key_vault_name: str = None):
        """
        Inicializa el administrador de configuración asíncrono.
        
        Args:
            environment (str, optional): Entorno actual (dev, prod, etc.)
            key_vault_name (str, optional): Nombre del Key Vault
        """
        self.environment = environment or os.getenv("APP_ENV", "dev")
        self.key_vault_name = key_vault_name or os.getenv("KEY_VAULT_NAME")
        self._key_vault_client = None
        self._config_cache = {}
        self._lock = asyncio.Lock()
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
    
    async def _get_key_vault_client(self) -> AsyncSecretClient:
        """
        Obtiene o inicializa el cliente asíncrono de Key Vault.
        
        Returns:
            AsyncSecretClient: Cliente asíncrono configurado para Key Vault
            
        Raises:
            ConfigurationError: Si no se puede acceder al Key Vault
        """
        async with self._lock:
            if self._key_vault_client is None:
                if not self.key_vault_name:
                    raise ConfigurationError(
                        "Nombre del Key Vault no configurado",
                        missing_config="KEY_VAULT_NAME"
                    )
                
                try:
                    authenticator = AsyncAzureAuthenticator()
                    vault_url = f"https://{self.key_vault_name}.vault.azure.net"
                    credential = await authenticator.get_credential()
                    self._key_vault_client = AsyncSecretClient(
                        vault_url=vault_url,
                        credential=credential
                    )
                    logger.info(f"Cliente asíncrono de Key Vault inicializado: {vault_url}")
                except Exception as e:
                    raise ConfigurationError(f"Error al inicializar Key Vault asíncrono: {e}")
                    
        return self._key_vault_client
    
    async def get_secret_from_key_vault(self, secret_name: str) -> str:
        """
        Obtiene un secreto desde Azure Key Vault de manera asíncrona.
        
        Args:
            secret_name (str): Nombre del secreto a recuperar
            
        Returns:
            str: Valor del secreto
            
        Raises:
            KeyVaultError: Si no se puede obtener el secreto
        """
        try:
            client = await self._get_key_vault_client()
            secret = await client.get_secret(secret_name)
            logger.info(f"Secreto '{secret_name}' obtenido exitosamente de manera asíncrona")
            return secret.value
        except Exception as e:
            logger.error(f"Error al obtener secreto asíncrono '{secret_name}': {e}")
            raise KeyVaultError(
                f"No se pudo obtener el secreto '{secret_name}': {e}",
                secret_name=secret_name
            )
    
    async def get_config_value(self, key: str, required: bool = True, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración de manera asíncrona desde variables de entorno o Key Vault.
        
        La búsqueda se realiza en el siguiente orden:
        1. Variables de entorno (ej: COSMOS_URI)
        2. Key Vault del entorno actual (ej: cosmos-uri)
        3. Valor por defecto si se proporciona
        
        Args:
            key (str): Clave de configuración a buscar
            required (bool): Si es requerido el valor
            default (Any): Valor por defecto si no se encuentra
            
        Returns:
            Any: Valor de configuración encontrado
            
        Raises:
            ConfigurationError: Si el valor es requerido y no se encuentra
        """
        # Verificar caché primero
        cache_key = f"{self.environment}:{key}"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        # 1. Variable de entorno (estándar, sin prefijo de ambiente)
        env_key = key.upper()
        value = os.getenv(env_key)
        
        if value:
            logger.debug(f"Configuración encontrada en variable de entorno: {env_key}")
            self._config_cache[cache_key] = value
            return value
        
        # 2. Key Vault (sin prefijo de ambiente, el ambiente se maneja por Key Vault diferente)
        secret_name = key.lower().replace('_', '-')
        try:
            value = await self.get_secret_from_key_vault(secret_name)
            if value:
                logger.debug(f"Configuración encontrada en Key Vault asíncrono: {secret_name}")
                self._config_cache[cache_key] = value
                return value
        except KeyVaultError:
            logger.debug(f"No se encontró secreto en Key Vault asíncrono: {secret_name}")
        
        # 3. Valor por defecto
        if default is not None:
            logger.debug(f"Usando valor por defecto para {key}: {default}")
            self._config_cache[cache_key] = default
            return default
        
        # Si es requerido y no se encontró, lanzar error
        if required:
            raise ConfigurationError(
                f"Configuración requerida no encontrada: {key}. "
                f"Asegúrate de configurar la variable {env_key} o el secreto {secret_name} en Key Vault.",
                missing_config=key
            )
        
        return None
    
    async def get_cosmos_config(self) -> Dict[str, str]:
        """
        Obtiene la configuración específica para Azure Cosmos DB de manera asíncrona.
        
        Returns:
            Dict[str, str]: Diccionario con configuración de Cosmos DB
        """
        config_tasks = [
            self.get_config_value("COSMOS_URI"),
            self.get_config_value("COSMOS_KEY"),
            self.get_config_value("COSMOS_DATABASE"),
            self.get_config_value("COSMOS_CONTAINER"),
            self.get_config_value("COSMOS_PARTITION", required=False, default="/id")
        ]
        
        uri, key, database_name, container_name, partition_key = await asyncio.gather(*config_tasks)
        
        return {
            "uri": uri,
            "key": key,
            "database_name": database_name,
            "container_name": container_name,
            "partition_key": partition_key
        }
    
    async def get_openai_config(self) -> Dict[str, str]:
        """
        Obtiene la configuración específica para Azure OpenAI de manera asíncrona.
        
        Returns:
            Dict[str, str]: Diccionario con configuración de OpenAI
        """
        config_tasks = [
            self.get_config_value("OPENAI_ENDPOINT"),
            self.get_config_value("OPENAI_API_KEY"),
            self.get_config_value("OPENAI_API_VERSION", required=False, default="2024-02-01"),
            self.get_config_value("OPENAI_DEPLOYMENT_NAME")
        ]
        
        endpoint, api_key, api_version, deployment_name = await asyncio.gather(*config_tasks)
        
        return {
            "endpoint": endpoint,
            "api_key": api_key,
            "api_version": api_version,
            "deployment_name": deployment_name
        }
    
    async def get_storage_config(self) -> Dict[str, str]:
        """
        Obtiene la configuración específica para Azure Blob Storage de manera asíncrona.
        
        Returns:
            Dict[str, str]: Diccionario con configuración de Blob Storage
        """
        config_tasks = [
            self.get_config_value("STORAGE_CONNECTION_STRING"),
            self.get_config_value("STORAGE_ACCOUNT_NAME"),
            self.get_config_value("STORAGE_ACCOUNT_KEY"),
            self.get_config_value("STORAGE_CONTAINER_NAME")
        ]
        
        connection_string, account_name, account_key, container_name = await asyncio.gather(*config_tasks)
        
        return {
            "connection_string": connection_string,
            "account_name": account_name,
            "account_key": account_key,
            "container_name": container_name
        }
    
    def clear_cache(self):
        """
        Limpia el caché de configuración.
        """
        self._config_cache.clear()
        logger.info("Caché de configuración asíncrono limpiado")
    
    def set_environment(self, environment: str):
        """
        Cambia el entorno y limpia el caché.
        
        Args:
            environment (str): Nuevo entorno a configurar
        """
        self.environment = environment
        self.clear_cache()
        logger.info(f"Entorno asíncrono cambiado a: {environment}")
    
    async def close(self):
        """
        Cierra el cliente de Key Vault y libera recursos.
        """
        if self._key_vault_client:
            await self._key_vault_client.close()
            logger.info("Cliente asíncrono de Key Vault cerrado correctamente")
            
    # Configuración Recurso Datalake
    async def get_datalake_config(self) -> dict:
        """
        Devuelve la configuración de Azure Data Lake (asíncrona).
        """
        return {
            "account_name": await self.get_config_value("DATALAKE_ACCOUNT_NAME"),
            "file_system_name": await self.get_config_value("DATALAKE_FILE_SYSTEM_NAME"),
            "account_key": await self.get_config_value("DATALAKE_ACCOUNT_KEY")
        } 
    
    # Configuración Recurso Blob Storage
    async def get_blob_storage_config(self) -> dict:
        """
        Devuelve la configuración de Azure Blob Storage (asíncrona).
        """
        return {
            "account_name": await self.get_config_value("BLOB_STORAGE_ACCOUNT_NAME"),
            "file_system_name": await self.get_config_value("BLOB_STORAGE_FILE_SYSTEM_NAME"),
            "account_key": await self.get_config_value("BLOB_STORAGE_ACCOUNT_KEY")
        }

    # Dentro de AsyncConfigManager en config.py
    async def get_search_config(self) -> Dict[str, str]:
        """
        Obtiene la configuración para Azure Cognitive Search (asíncrono).
        """
        config_tasks = [
            self.get_config_value("SEARCH_ENDPOINT"),
            self.get_config_value("SEARCH_API_KEY"),
            self.get_config_value("SEARCH_INDEX_NAME")
        ]
        endpoint, api_key, index_name = await asyncio.gather(*config_tasks)

        return {
            "endpoint": endpoint,
            "api_key": api_key,
            "index_name": index_name
        }
