"""
Administrador de contenedores para Azure Cosmos DB.
Permite la creación y gestión dinámica de contenedores dentro de bases de datos.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from azure.cosmos import PartitionKey, ThroughputProperties
from azure.cosmos.exceptions import CosmosHttpResponseError

from .database_manager import AsyncDatabaseManager
from ..common.config import AsyncConfigManager
from ..common.exceptions import CosmosDBError

logger = logging.getLogger(__name__)


class ContainerConfig:
    """
    Configuración para la creación de contenedores.
    Encapsula todas las opciones de configuración en una clase reutilizable.
    """
    
    def __init__(
        self,
        container_name: str,
        partition_key_path: str,
        throughput: Optional[Union[int, ThroughputProperties]] = None,
        indexing_policy: Optional[Dict[str, Any]] = None,
        unique_key_policy: Optional[Dict[str, Any]] = None,
        conflict_resolution_policy: Optional[Dict[str, Any]] = None,
        default_ttl: Optional[int] = None
    ):
        """
        Inicializa la configuración del contenedor.
        
        Args:
            container_name (str): Nombre del contenedor
            partition_key_path (str): Ruta de la clave de partición (ej: "/id", "/userId")
            throughput (Optional[Union[int, ThroughputProperties]]): Configuración de rendimiento
            indexing_policy (Optional[Dict]): Política de indexación personalizada
            unique_key_policy (Optional[Dict]): Política de claves únicas
            conflict_resolution_policy (Optional[Dict]): Política de resolución de conflictos
            default_ttl (Optional[int]): TTL por defecto en segundos
        """
        self.container_name = container_name
        self.partition_key_path = partition_key_path
        self.throughput = throughput
        self.indexing_policy = indexing_policy
        self.unique_key_policy = unique_key_policy
        self.conflict_resolution_policy = conflict_resolution_policy
        self.default_ttl = default_ttl
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la configuración a un diccionario para la API de Cosmos DB.
        
        Returns:
            Dict[str, Any]: Configuración en formato de diccionario
        """
        config = {
            "id": self.container_name,
            "partition_key": PartitionKey(path=self.partition_key_path)
        }
        
        if self.indexing_policy:
            config["indexing_policy"] = self.indexing_policy
        
        if self.unique_key_policy:
            config["unique_key_policy"] = self.unique_key_policy
        
        if self.conflict_resolution_policy:
            config["conflict_resolution_policy"] = self.conflict_resolution_policy
        
        # Nota: TTL se debe configurar después de crear el contenedor
        # No se puede pasar directamente en create_container
        
        return config


class AsyncContainerManager:
    """
    Administrador asíncrono para la gestión de contenedores en Azure Cosmos DB.
    
    Permite crear, configurar y administrar múltiples contenedores de manera dinámica,
    optimizando costos y rendimiento según las necesidades específicas.
    """
    
    def __init__(
        self, 
        database_manager: AsyncDatabaseManager = None,
        environment: str = None, 
        config_manager: AsyncConfigManager = None
    ):
        """
        Inicializa el administrador de contenedores.
        
        Args:
            database_manager (AsyncDatabaseManager, optional): Administrador de bases de datos
            environment (str, optional): Entorno de ejecución
            config_manager (AsyncConfigManager, optional): Administrador de configuración
        """
        self.environment = environment or "dev"
        self.config_manager = config_manager or AsyncConfigManager(self.environment)
        self.database_manager = database_manager or AsyncDatabaseManager(
            environment=self.environment,
            config_manager=self.config_manager
        )
        
        self._container_cache = {}
        
        logger.info(f"ContainerManager asíncrono creado para entorno: {self.environment}")
    
    async def create_container(
        self,
        database_name: str,
        container_config: ContainerConfig,
        if_not_exists: bool = True
    ) -> Dict[str, Any]:
        """
        Crea un nuevo contenedor en la base de datos especificada.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_config (ContainerConfig): Configuración del contenedor
            if_not_exists (bool): Si True, no falla si el contenedor ya existe
            
        Returns:
            Dict[str, Any]: Información del contenedor creado
            
        Raises:
            CosmosDBError: Si ocurre un error al crear el contenedor
        """
        try:
            logger.info(f"Creando contenedor '{container_config.container_name}' en base de datos '{database_name}'")
            
            # Obtener referencia a la base de datos
            database = await self.database_manager.get_database(database_name)
            
            # Preparar configuración del contenedor
            container_options = container_config.to_dict()
            
            # Configurar throughput si se especifica
            throughput_options = {}
            if container_config.throughput is not None:
                if isinstance(container_config.throughput, int):
                    throughput_options["offer_throughput"] = container_config.throughput
                    logger.info(f"Configurando {container_config.throughput} RU/s para el contenedor")
                else:
                    # ThroughputProperties para configuración avanzada
                    throughput_options["offer_throughput"] = container_config.throughput
                    logger.info(f"Configurando rendimiento avanzado para el contenedor")
            
            # Crear contenedor
            if if_not_exists:
                container = await database.create_container_if_not_exists(
                    **container_options,
                    **throughput_options
                )
                logger.info(f"Contenedor '{container_config.container_name}' creado o ya existía")
            else:
                container = await database.create_container(
                    **container_options,
                    **throughput_options
                )
                logger.info(f"Contenedor '{container_config.container_name}' creado exitosamente")
            
            # Configurar TTL si está especificado (post-creación)
            if container_config.default_ttl is not None:
                try:
                    # Obtener propiedades actuales del contenedor
                    container_properties = await container.read()
                    container_properties["defaultTtl"] = container_config.default_ttl
                    
                    # Actualizar el contenedor con TTL
                    await container.replace_container(container_properties)
                    logger.info(f"TTL configurado: {container_config.default_ttl} segundos")
                except Exception as ttl_error:
                    logger.warning(f"No se pudo configurar TTL: {ttl_error}")
            
            # Agregar al cache
            cache_key = f"{database_name}/{container_config.container_name}"
            self._container_cache[cache_key] = container
            
            # Obtener información del contenedor
            container_info = {
                "id": container.id,
                "database_name": database_name,
                "partition_key_path": container_config.partition_key_path,
                "created": True,
                "container_link": container.container_link,
                "throughput_configured": container_config.throughput is not None,
                "ttl_configured": container_config.default_ttl is not None
            }
            
            return container_info
            
        except CosmosHttpResponseError as e:
            logger.error(f"Error al crear contenedor '{container_config.container_name}': {e}")
            raise CosmosDBError(
                f"Error al crear contenedor '{container_config.container_name}': {e.message}",
                status_code=e.status_code
            )
    
    async def create_container_simple(
        self,
        database_name: str,
        container_name: str,
        partition_key_path: str,
        throughput: Optional[int] = None,
        if_not_exists: bool = True
    ) -> Dict[str, Any]:
        """
        Método simplificado para crear un contenedor con configuración básica.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor
            partition_key_path (str): Ruta de la clave de partición
            throughput (Optional[int]): RU/s dedicadas (opcional)
            if_not_exists (bool): Si True, no falla si el contenedor ya existe
            
        Returns:
            Dict[str, Any]: Información del contenedor creado
        """
        container_config = ContainerConfig(
            container_name=container_name,
            partition_key_path=partition_key_path,
            throughput=throughput
        )
        
        return await self.create_container(
            database_name=database_name,
            container_config=container_config,
            if_not_exists=if_not_exists
        )
    
    async def get_container(self, database_name: str, container_name: str):
        """
        Obtiene una referencia a un contenedor existente.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor
            
        Returns:
            Container: Referencia al contenedor
            
        Raises:
            CosmosDBError: Si el contenedor no existe
        """
        cache_key = f"{database_name}/{container_name}"
        
        # Verificar cache primero
        if cache_key in self._container_cache:
            return self._container_cache[cache_key]
        
        try:
            # Obtener base de datos
            database = await self.database_manager.get_database(database_name)
            
            # Obtener contenedor
            container = database.get_container_client(container_name)
            
            # Verificar que existe intentando obtener sus propiedades
            await container.read()
            
            # Agregar al cache
            self._container_cache[cache_key] = container
            
            logger.info(f"Contenedor '{container_name}' obtenido exitosamente")
            return container
            
        except CosmosHttpResponseError as e:
            if e.status_code == 404:
                logger.error(f"Contenedor '{container_name}' no encontrado en base de datos '{database_name}'")
                raise CosmosDBError(
                    f"Contenedor '{container_name}' no existe en base de datos '{database_name}'",
                    status_code=404
                )
            logger.error(f"Error al obtener contenedor '{container_name}': {e}")
            raise CosmosDBError(
                f"Error al obtener contenedor '{container_name}': {e.message}",
                status_code=e.status_code
            )
    
    async def list_containers(self, database_name: str) -> List[Dict[str, Any]]:
        """
        Lista todos los contenedores en una base de datos.
        
        Args:
            database_name (str): Nombre de la base de datos
            
        Returns:
            List[Dict[str, Any]]: Lista de información de contenedores
        """
        try:
            database = await self.database_manager.get_database(database_name)
            
            containers = []
            async for container in database.list_containers():
                container_info = {
                    "id": container["id"],
                    "database_name": database_name,
                    "self_link": container.get("_self"),
                    "resource_id": container.get("_rid"),
                    "timestamp": container.get("_ts"),
                    "partition_key": container.get("partitionKey")
                }
                containers.append(container_info)
            
            logger.info(f"Encontrados {len(containers)} contenedores en base de datos '{database_name}'")
            return containers
            
        except CosmosDBError:
            raise
        except Exception as e:
            logger.error(f"Error al listar contenedores en base de datos '{database_name}': {e}")
            raise CosmosDBError(f"Error al listar contenedores: {e}")
    
    async def delete_container(self, database_name: str, container_name: str) -> bool:
        """
        Elimina un contenedor y todos sus documentos.
        
        ADVERTENCIA: Esta operación es irreversible y eliminará todos los datos.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Raises:
            CosmosDBError: Si ocurre un error al eliminar
        """
        try:
            logger.warning(f"ELIMINANDO contenedor: {container_name} en {database_name} (IRREVERSIBLE)")
            
            # Obtener referencia a la base de datos
            database = await self.database_manager.get_database(database_name)
            
            # Eliminar contenedor usando el método del database
            await database.delete_container(container_name)
            
            # Remover del cache
            cache_key = f"{database_name}/{container_name}"
            if cache_key in self._container_cache:
                del self._container_cache[cache_key]
            
            logger.info(f"Contenedor '{container_name}' eliminado exitosamente")
            return True
            
        except CosmosHttpResponseError as e:
            if e.status_code == 404:
                logger.warning(f"Contenedor '{container_name}' no encontrado para eliminar")
                return False
            logger.error(f"Error al eliminar contenedor '{container_name}': {e}")
            raise CosmosDBError(
                f"Error al eliminar contenedor '{container_name}': {e.message}",
                status_code=e.status_code
            )
    
    async def get_container_throughput(
        self, 
        database_name: str, 
        container_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene la configuración de rendimiento de un contenedor.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor
            
        Returns:
            Optional[Dict[str, Any]]: Información de rendimiento o None si no tiene configurado
        """
        try:
            container = await self.get_container(database_name, container_name)
            
            # Intentar obtener la oferta de rendimiento
            try:
                throughput = await container.get_throughput()
                
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
            logger.error(f"Error al obtener rendimiento del contenedor '{container_name}': {e}")
            raise CosmosDBError(f"Error al obtener rendimiento: {e}")
    
    async def close(self):
        """
        Cierra el administrador y libera recursos.
        """
        if self.database_manager:
            await self.database_manager.close()
        logger.info("ContainerManager cerrado exitosamente")
    
    async def __aenter__(self):
        """Soporte para context manager asíncrono."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup automático al salir del context manager."""
        await self.close() 