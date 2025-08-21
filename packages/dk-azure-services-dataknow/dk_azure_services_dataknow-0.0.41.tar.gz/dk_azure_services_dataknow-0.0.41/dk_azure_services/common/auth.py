"""
Módulo de autenticación centralizada para servicios de Azure.
"""

import asyncio
import logging
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from .exceptions import AzureServiceError

logger = logging.getLogger(__name__)


class AzureAuthenticator:
    """
    Clase para manejar la autenticación centralizada con Azure usando DefaultAzureCredential.
    
    Esta clase proporciona un punto único de autenticación para todos los servicios de Azure,
    siguiendo las mejores prácticas de seguridad.
    """
    
    _instance = None
    _credential = None
    
    def __new__(cls):
        """
        Implementa el patrón singleton para asegurar una sola instancia del autenticador.
        """
        if cls._instance is None:
            cls._instance = super(AzureAuthenticator, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Inicializa el autenticador Azure si no ha sido inicializado previamente.
        """
        if self._credential is None:
            self._initialize_credential()
    
    def _initialize_credential(self):
        """
        Inicializa las credenciales usando DefaultAzureCredential.
        
        DefaultAzureCredential intenta múltiples métodos de autenticación:
        - Environment variables
        - Managed Identity
        - Visual Studio Code
        - Azure CLI
        - Azure PowerShell
        - Interactive browser
        """
        try:
            self._credential = DefaultAzureCredential()
            logger.info("Credenciales de Azure inicializadas correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar credenciales de Azure: {e}")
            raise AzureServiceError(f"Fallo en la autenticación de Azure: {e}")
    
    def get_credential(self):
        """
        Obtiene las credenciales de Azure inicializadas.
        
        Returns:
            DefaultAzureCredential: Objeto de credenciales de Azure
            
        Raises:
            AzureServiceError: Si las credenciales no están disponibles
        """
        if self._credential is None:
            raise AzureServiceError("Credenciales no inicializadas")
        
        return self._credential
    
    def test_authentication(self):
        """
        Prueba la autenticación obteniendo un token de acceso.
        
        Returns:
            bool: True si la autenticación es exitosa, False en caso contrario
        """
        try:
            credential = self.get_credential()
            # Intentamos obtener un token para verificar que la auth funciona
            token = credential.get_token("https://management.azure.com/.default")
            logger.info("Autenticación de Azure verificada exitosamente")
            return True
        except Exception as e:
            logger.error(f"Fallo en la verificación de autenticación: {e}")
            return False


class AsyncAzureAuthenticator:
    """
    Clase para manejar la autenticación asíncrona centralizada con Azure.
    
    Versión asíncrona del autenticador que proporciona credenciales optimizadas
    para operaciones concurrentes y de alto rendimiento.
    """
    
    _instance = None
    _credential = None
    _lock = None
    
    def __new__(cls):
        """
        Implementa el patrón singleton para asegurar una sola instancia del autenticador asíncrono.
        """
        if cls._instance is None:
            cls._instance = super(AsyncAzureAuthenticator, cls).__new__(cls)
            cls._lock = asyncio.Lock()
        return cls._instance
    
    def __init__(self):
        """
        Inicializa el autenticador Azure asíncrono.
        """
        if self._credential is None:
            # La inicialización real se hace de manera lazy en get_credential
            pass
    
    async def _initialize_credential(self):
        """
        Inicializa las credenciales usando AsyncDefaultAzureCredential.
        
        AsyncDefaultAzureCredential proporciona los mismos métodos de autenticación
        pero optimizados para operaciones asíncronas.
        """
        async with self._lock:
            if self._credential is None:
                try:
                    self._credential = AsyncDefaultAzureCredential()
                    logger.info("Credenciales asíncronas de Azure inicializadas correctamente")
                except Exception as e:
                    logger.error(f"Error al inicializar credenciales asíncronas de Azure: {e}")
                    raise AzureServiceError(f"Fallo en la autenticación asíncrona de Azure: {e}")
    
    async def get_credential(self):
        """
        Obtiene las credenciales de Azure inicializadas de manera asíncrona.
        
        Returns:
            AsyncDefaultAzureCredential: Objeto de credenciales asíncronas de Azure
            
        Raises:
            AzureServiceError: Si las credenciales no están disponibles
        """
        if self._credential is None:
            await self._initialize_credential()
        
        return self._credential
    
    async def test_authentication(self):
        """
        Prueba la autenticación obteniendo un token de acceso de manera asíncrona.
        
        Returns:
            bool: True si la autenticación es exitosa, False en caso contrario
        """
        try:
            credential = await self.get_credential()
            # Intentamos obtener un token para verificar que la auth funciona
            token = await credential.get_token("https://management.azure.com/.default")
            logger.info("Autenticación asíncrona de Azure verificada exitosamente")
            return True
        except Exception as e:
            logger.error(f"Fallo en la verificación de autenticación asíncrona: {e}")
            return False
    
    async def close(self):
        """
        Cierra las credenciales asíncronas y libera recursos.
        """
        if self._credential:
            await self._credential.close()
            logger.info("Credenciales asíncronas cerradas correctamente") 