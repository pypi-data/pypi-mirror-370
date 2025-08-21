"""
Administrador de bases de datos para Azure Cosmos DB.
Permite la creación y gestión dinámica de bases de datos.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from azure.cosmos.aio import CosmosClient
from azure.cosmos import ThroughputProperties
from azure.cosmos.exceptions import CosmosHttpResponseError

from ..common.config import AsyncConfigManager
from ..common.auth import AsyncAzureAuthenticator
from ..common.exceptions import CosmosDBError, ConfigurationError

logger = logging.getLogger(__name__)


class AsyncDatabaseManager:
    """
    Administrador asíncrono para la gestión de bases de datos en Azure Cosmos DB.
    
    Permite crear, configurar y administrar múltiples bases de datos de manera dinámica,
    siguiendo las mejores prácticas de rendimiento y costos.
    """
    
    def __init__(self, environment: str = None, config_manager: AsyncConfigManager = None):
        """
        Inicializa el administrador de bases de datos con configuración segura por entorno.
        
        Args:
            environment (str, optional): Entorno de ejecución (dev, prod, etc.)
            config_manager (AsyncConfigManager, optional): Administrador de configuración personalizado
        """
        self.environment = environment or "dev"
        self.config_manager = config_manager or AsyncConfigManager(self.environment)
        
        # Variables para inicialización lazy
        self.config = None
        self.client = None
        self._initialized = False
        self._lock = asyncio.Lock()
        self._database_cache = {}
        
        logger.info(f"DatabaseManager asíncrono creado para entorno: {self.environment}")
    
    async def _ensure_initialized(self):
        """
        Asegura que el cliente esté inicializado antes de usar.
        """
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    await self._initialize()
    
    async def _initialize(self):
        """
        Inicializa el cliente Cosmos DB de manera asíncrona.
        """
        try:
            # Cargar configuración básica de Cosmos
            self.config = await self.config_manager.get_cosmos_config()
            
            # Inicializar cliente Cosmos (solo cliente, no recursos específicos)
            self.client = CosmosClient(self.config["uri"], self.config["key"])
            
            self._initialized = True
            logger.info(f"DatabaseManager asíncrono inicializado para entorno: {self.environment}")
        except Exception as e:
            logger.error(f"Error al inicializar DatabaseManager asíncrono: {e}")
            raise CosmosDBError(f"Fallo en la inicialización del DatabaseManager: {e}")
    
    async def create_database(
        self, 
        database_name: str,
        throughput: Optional[Union[int, ThroughputProperties]] = None,
        if_not_exists: bool = True
    ) -> Dict[str, Any]:
        """
        Crea una nueva base de datos en Cosmos DB de manera asíncrona.
        
        Args:
            database_name (str): Nombre de la base de datos a crear
            throughput (Optional[Union[int, ThroughputProperties]]): Configuración de rendimiento
                - None: Sin rendimiento dedicado (usa el del contenedor)
                - int: RU/s dedicadas (ej: 400, 1000)
                - ThroughputProperties: Configuración avanzada (autoscale, etc.)
            if_not_exists (bool): Si True, no falla si la base de datos ya existe
            
        Returns:
            Dict[str, Any]: Información de la base de datos creada
            
        Raises:
            CosmosDBError: Si ocurre un error al crear la base de datos
        """
        await self._ensure_initialized()
        
        try:
            logger.info(f"Creando base de datos: {database_name}")
            
            # Preparar opciones de creación
            options = {}
            if throughput is not None:
                if isinstance(throughput, int):
                    options["offer_throughput"] = throughput
                    logger.info(f"Configurando {throughput} RU/s dedicadas para la base de datos")
                else:
                    # ThroughputProperties para configuración avanzada
                    options["offer_throughput"] = throughput
                    logger.info(f"Configurando rendimiento avanzado para la base de datos")
            
            # Crear base de datos
            if if_not_exists:
                database = await self.client.create_database_if_not_exists(
                    id=database_name,
                    **options
                )
                logger.info(f"Base de datos '{database_name}' creada o ya existía")
            else:
                database = await self.client.create_database(
                    id=database_name,
                    **options
                )
                logger.info(f"Base de datos '{database_name}' creada exitosamente")
            
            # Agregar al cache
            self._database_cache[database_name] = database
            
            # Obtener información de la base de datos
            db_info = {
                "id": database.id,
                "created": True,
                "self_link": database.database_link,
                "throughput_configured": throughput is not None
            }
            
            return db_info
            
        except CosmosHttpResponseError as e:
            logger.error(f"Error al crear base de datos '{database_name}': {e}")
            raise CosmosDBError(
                f"Error al crear base de datos '{database_name}': {e.message}",
                status_code=e.status_code
            )
    
    async def get_database(self, database_name: str):
        """
        Obtiene una referencia a una base de datos existente.
        
        Args:
            database_name (str): Nombre de la base de datos
            
        Returns:
            Database: Referencia a la base de datos
            
        Raises:
            CosmosDBError: Si la base de datos no existe
        """
        await self._ensure_initialized()
        
        # Verificar cache primero
        if database_name in self._database_cache:
            return self._database_cache[database_name]
        
        try:
            # Obtener base de datos
            database = self.client.get_database_client(database_name)
            
            # Verificar que existe intentando obtener sus propiedades
            await database.read()
            
            # Agregar al cache
            self._database_cache[database_name] = database
            
            logger.info(f"Base de datos '{database_name}' obtenida exitosamente")
            return database
            
        except CosmosHttpResponseError as e:
            if e.status_code == 404:
                logger.error(f"Base de datos '{database_name}' no encontrada")
                raise CosmosDBError(
                    f"Base de datos '{database_name}' no existe",
                    status_code=404
                )
            logger.error(f"Error al obtener base de datos '{database_name}': {e}")
            raise CosmosDBError(
                f"Error al obtener base de datos '{database_name}': {e.message}",
                status_code=e.status_code
            )
    
    async def list_databases(self) -> List[Dict[str, Any]]:
        """
        Lista todas las bases de datos en la cuenta de Cosmos DB.
        
        Returns:
            List[Dict[str, Any]]: Lista de información de bases de datos
        """
        await self._ensure_initialized()
        
        try:
            databases = []
            async for database in self.client.list_databases():
                db_info = {
                    "id": database["id"],
                    "self_link": database.get("_self"),
                    "resource_id": database.get("_rid"),
                    "timestamp": database.get("_ts")
                }
                databases.append(db_info)
            
            logger.info(f"Encontradas {len(databases)} bases de datos")
            return databases
            
        except CosmosHttpResponseError as e:
            logger.error(f"Error al listar bases de datos: {e}")
            raise CosmosDBError(
                f"Error al listar bases de datos: {e.message}",
                status_code=e.status_code
            )
    
    async def delete_database(self, database_name: str) -> bool:
        """
        Elimina una base de datos y todos sus contenedores.
        
        ADVERTENCIA: Esta operación es irreversible y eliminará todos los datos.
        
        Args:
            database_name (str): Nombre de la base de datos a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Raises:
            CosmosDBError: Si ocurre un error al eliminar
        """
        await self._ensure_initialized()
        
        try:
            logger.warning(f"ELIMINANDO base de datos: {database_name} (IRREVERSIBLE)")
            
            # Obtener referencia a la base de datos
            database = self.client.get_database_client(database_name)
            
            # Eliminar base de datos
            await self.client.delete_database(database_name)
            
            # Remover del cache
            if database_name in self._database_cache:
                del self._database_cache[database_name]
            
            logger.info(f"Base de datos '{database_name}' eliminada exitosamente")
            return True
            
        except CosmosHttpResponseError as e:
            if e.status_code == 404:
                logger.warning(f"Base de datos '{database_name}' no encontrada para eliminar")
                return False
            logger.error(f"Error al eliminar base de datos '{database_name}': {e}")
            raise CosmosDBError(
                f"Error al eliminar base de datos '{database_name}': {e.message}",
                status_code=e.status_code
            )
    
    async def get_database_throughput(self, database_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la configuración de rendimiento de una base de datos.
        
        Args:
            database_name (str): Nombre de la base de datos
            
        Returns:
            Optional[Dict[str, Any]]: Información de rendimiento o None si no tiene configurado
        """
        await self._ensure_initialized()
        
        try:
            database = await self.get_database(database_name)
            
            # Intentar obtener la oferta de rendimiento
            try:
                throughput = await database.get_throughput()
                
                throughput_info = {
                    "offer_throughput": throughput.offer_throughput,
                    "is_autopilot": hasattr(throughput, 'autopilot_settings') and throughput.autopilot_settings is not None,
                    "properties": throughput
                }
                
                if throughput_info["is_autopilot"]:
                    throughput_info["autopilot_max_throughput"] = throughput.autopilot_settings.max_throughput
                
                return throughput_info
                
            except CosmosHttpResponseError as e:
                if e.status_code == 400:  # No throughput configured
                    return None
                raise
                
        except CosmosDBError:
            raise
        except Exception as e:
            logger.error(f"Error al obtener rendimiento de base de datos '{database_name}': {e}")
            raise CosmosDBError(f"Error al obtener rendimiento: {e}")
    
    async def close(self):
        """
        Cierra el cliente y libera recursos.
        """
        if self.client:
            await self.client.close()
            logger.info("DatabaseManager cerrado exitosamente")
    
    async def __aenter__(self):
        """Soporte para context manager asíncrono."""
        await self._ensure_initialized()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup automático al salir del context manager."""
        await self.close() 