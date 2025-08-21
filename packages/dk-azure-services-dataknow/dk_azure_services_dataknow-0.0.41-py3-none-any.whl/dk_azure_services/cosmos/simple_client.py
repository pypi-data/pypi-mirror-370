"""
Cliente simplificado para Azure Cosmos DB.
Máxima simplicidad - mínima configuración.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.core import MatchConditions

from ..common.config import AsyncConfigManager
from ..common.exceptions import CosmosDBError

logger = logging.getLogger(__name__)


class AsyncCosmosDBClient:
    """
    Cliente simplificado para Azure Cosmos DB con partition key parametrizable.
    """
    def __init__(self, environment: str = "dev", partition_key_path: str = "/id"):
        """
        Inicializa el cliente Cosmos DB.
        Args:
            environment (str): Entorno (dev, prod, test). Por defecto "dev"
            partition_key_path (str): Ruta de la partition key (ej: "/id", "/user_id"). Por defecto "/id"
        """
        self.environment = environment
        self.partition_key_path = partition_key_path
        self.config_manager = AsyncConfigManager(environment)
        # Variables para inicialización lazy
        self.config = None
        self.client = None
        self._initialized = False
        self._lock = asyncio.Lock()
        # Cache para recursos
        self._database_cache = {}
        self._container_cache = {}
        logger.info(f"Cliente Cosmos DB inicializado para entorno: {environment} y partition_key_path: {partition_key_path}")
    
    async def _ensure_initialized(self):
        """Asegura que el cliente esté inicializado."""
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    await self._initialize()
    
    async def _initialize(self):
        """Inicializa el cliente de manera asíncrona."""
        try:
            self.config = await self.config_manager.get_cosmos_config()
            self.client = CosmosClient(self.config["uri"], self.config["key"])
            self._initialized = True
            logger.info("Cliente Cosmos DB inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar cliente: {e}")
            raise CosmosDBError(f"Error de inicialización: {e}")
    
    # =============================================================================
    # GESTIÓN DE BASES DE DATOS
    # =============================================================================
    
    async def create_database(
        self, 
        database_name: str,
        throughput: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Crea una base de datos.
        
        Args:
            database_name (str): Nombre de la base de datos
            throughput (int, optional): RU/s dedicadas (ej: 400, 1000)
            
        Returns:
            Dict: Información de la base de datos creada
            
        Example:
            await cosmos.create_database("mi_app")
            await cosmos.create_database("mi_app", throughput=400)
        """
        await self._ensure_initialized()
        
        try:
            options = {}
            if throughput:
                options["offer_throughput"] = throughput
            
            database = await self.client.create_database_if_not_exists(
                id=database_name,
                **options
            )
            
            self._database_cache[database_name] = database
            
            logger.info(f"Base de datos '{database_name}' creada/verificada")
            return {
                "name": database_name,
                "created": True,
                "throughput": throughput
            }
            
        except Exception as e:
            logger.error(f"Error al crear base de datos '{database_name}': {e}")
            raise CosmosDBError(f"Error al crear base de datos: {e}")
    
    async def list_databases(self) -> List[Dict[str, Any]]:
        """
        Lista todas las bases de datos.
        
        Returns:
            List[Dict]: Lista de bases de datos
            
        Example:
            databases = await cosmos.list_databases()
            for db in databases:
                print(f"Base de datos: {db['name']}")
        """
        await self._ensure_initialized()
        
        try:
            databases = []
            async for db in self.client.list_databases():
                databases.append({
                    "name": db["id"],
                    "link": db.get("_self")
                })
            
            logger.info(f"Encontradas {len(databases)} bases de datos")
            return databases
            
        except Exception as e:
            logger.error(f"Error al listar bases de datos: {e}")
            raise CosmosDBError(f"Error al listar bases de datos: {e}")
    
    async def delete_database(self, database_name: str) -> bool:
        """
        Elimina una base de datos.
        
        Args:
            database_name (str): Nombre de la base de datos
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Example:
            await cosmos.delete_database("base_vieja")
        """
        await self._ensure_initialized()
        
        try:
            await self.client.delete_database(database_name)
            
            if database_name in self._database_cache:
                del self._database_cache[database_name]
            
            logger.info(f"Base de datos '{database_name}' eliminada")
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar base de datos '{database_name}': {e}")
            raise CosmosDBError(f"Error al eliminar base de datos: {e}")
    
    # =============================================================================
    # GESTIÓN DE CONTENEDORES
    # =============================================================================
    
    async def create_container(
        self,
        database_name: str,
        container_name: str,
        partition_key: Optional[str] = None,
        throughput: Optional[int] = None,
        ttl: Optional[int] = None,
        indexing_policy: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Crea un contenedor.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor
            partition_key (str, optional): Clave de partición (ej: "/id", "/user_id"). Si no se especifica, usa la del cliente
            throughput (int, optional): RU/s dedicadas
            ttl (int, optional): TTL en segundos (ej: 86400 para 24 horas)
            indexing_policy (Dict, optional): Política de indexación
            
        Returns:
            Dict: Información del contenedor creado
            
        Example:
            # Contenedor básico
            await cosmos.create_container("mi_app", "users")
            
            # Contenedor con configuración avanzada
            await cosmos.create_container(
                "mi_app", "logs", "/date",
                throughput=400,
                ttl=86400,
                indexing_policy={
                    "includedPaths": ["/timestamp/?", "/level/?"],
                    "excludedPaths": ["/message/*"]
                }
            )
        """
        await self._ensure_initialized()
        
        try:
            # Obtener o crear base de datos
            if database_name not in self._database_cache:
                database = await self.client.create_database_if_not_exists(id=database_name)
                self._database_cache[database_name] = database
            else:
                database = self._database_cache[database_name]
            
            # Configurar opciones del contenedor
            pk_path = partition_key if partition_key is not None else self.partition_key_path
            container_options = {
                "id": container_name,
                "partition_key": PartitionKey(path=pk_path)
            }
            
            if throughput:
                container_options["offer_throughput"] = throughput
            
            if indexing_policy:
                container_options["indexing_policy"] = indexing_policy
            
            # Crear contenedor
            container = await database.create_container_if_not_exists(**container_options)
            
            # Configurar TTL si se especifica
            if ttl:
                try:
                    properties = await container.read()
                    properties["defaultTtl"] = ttl
                    await container.replace_container(properties)
                    logger.info(f"TTL configurado: {ttl} segundos")
                except Exception as ttl_error:
                    logger.warning(f"No se pudo configurar TTL: {ttl_error}")
            
            # Cache del contenedor
            cache_key = f"{database_name}/{container_name}"
            self._container_cache[cache_key] = container
            
            logger.info(f"Contenedor '{container_name}' creado/verificado en '{database_name}'")
            return {
                "name": container_name,
                "database": database_name,
                "partition_key": pk_path,
                "created": True,
                "throughput": throughput,
                "ttl": ttl
            }
            
        except Exception as e:
            logger.error(f"Error al crear contenedor '{container_name}': {e}")
            raise CosmosDBError(f"Error al crear contenedor: {e}")
    
    async def list_containers(self, database_name: str) -> List[Dict[str, Any]]:
        """
        Lista todos los contenedores en una base de datos.
        
        Args:
            database_name (str): Nombre de la base de datos
            
        Returns:
            List[Dict]: Lista de contenedores
            
        Example:
            containers = await cosmos.list_containers("mi_app")
            for container in containers:
                print(f"Contenedor: {container['name']}")
        """
        await self._ensure_initialized()
        
        try:
            if database_name not in self._database_cache:
                database = await self.client.create_database_if_not_exists(id=database_name)
                self._database_cache[database_name] = database
            else:
                database = self._database_cache[database_name]
            
            containers = []
            async for container in database.list_containers():
                containers.append({
                    "name": container["id"],
                    "partition_key": container.get("partitionKey", {}).get("paths", []),
                    "link": container.get("_self")
                })
            
            logger.info(f"Encontrados {len(containers)} contenedores en '{database_name}'")
            return containers
            
        except Exception as e:
            logger.error(f"Error al listar contenedores: {e}")
            raise CosmosDBError(f"Error al listar contenedores: {e}")
    
    async def delete_container(self, database_name: str, container_name: str) -> bool:
        """
        Elimina un contenedor.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Example:
            await cosmos.delete_container("mi_app", "contenedor_viejo")
        """
        await self._ensure_initialized()
        
        try:
            if database_name not in self._database_cache:
                database = await self.client.create_database_if_not_exists(id=database_name)
                self._database_cache[database_name] = database
            else:
                database = self._database_cache[database_name]
            
            container = database.get_container_client(container_name)
            await container.delete_container()
            
            # Limpiar cache
            cache_key = f"{database_name}/{container_name}"
            if cache_key in self._container_cache:
                del self._container_cache[cache_key]
            
            logger.info(f"Contenedor '{container_name}' eliminado de '{database_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar contenedor: {e}")
            raise CosmosDBError(f"Error al eliminar contenedor: {e}")
    
    # =============================================================================
    # OPERACIONES DE DOCUMENTOS
    # =============================================================================
    
    async def create_document(
        self,
        database_name: str,
        container_name: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crea un documento. El valor de partition key debe estar incluido en el documento
        según la ruta especificada en partition_key_path.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor
            data (Dict): Datos del documento (debe incluir el campo de partition key)
        
        Returns:
            Dict: Documento creado
            
        Example:
            # Si partition_key_path="/id"
            doc = await cosmos.create_document("mi_app", "users", {
                "id": "user_123",
                "name": "Juan Pérez"
            })
            
            # Si partition_key_path="/partition_key"
            doc = await cosmos.create_document("mi_app", "users", {
                "id": "user_123",
                "name": "Juan Pérez",
                "partition_key": "user_123"
            })
        """
        await self._ensure_initialized()
        
        try:
            # Obtener contenedor
            container = await self._get_container(database_name, container_name)
            
            # Generar ID si no existe
            if "id" not in data:
                data["id"] = str(uuid.uuid4())
            
            # Crear el documento
            result = await container.create_item(body=data)
            
            logger.info(f"Documento creado en '{database_name}/{container_name}' con ID: {result['id']}")
            return result
            
        except Exception as e:
            logger.error(f"Error al crear documento: {e}")
            raise CosmosDBError(f"Error al crear documento: {e}")
    
    async def read_document(
        self,
        database_name: str,
        container_name: str,
        doc_id: str,
        partition_key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Lee un documento por ID.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor
            doc_id (str): ID del documento
            partition_key (str, optional): Clave de partición
            
        Returns:
            Dict: Documento encontrado o None si no existe
            
        Example:
            # Leer documento
            doc = await cosmos.read_document("mi_app", "users", "user_123")
            if doc:
                print(f"Usuario: {doc['name']}")
            else:
                print("Usuario no encontrado")
        """
        await self._ensure_initialized()
        
        try:
            container = await self._get_container(database_name, container_name)
            properties = await container.read()
            partition_key_paths = properties.get("partitionKey", {}).get("paths", [])
            if partition_key_paths:
                pk = partition_key if partition_key is not None else doc_id
                document = await container.read_item(
                    item=doc_id,
                    partition_key=pk
                )
            else:
                document = await container.read_item(
                    item=doc_id
                )
            logger.info(f"Documento leído: {doc_id}")
            return document
            
        except CosmosHttpResponseError as e:
            if e.status_code == 404:
                logger.warning(f"Documento no encontrado: {doc_id}")
                return None
            raise CosmosDBError(f"Error al leer documento: {e.message}")
        except Exception as e:
            logger.error(f"Error al leer documento: {e}")
            raise CosmosDBError(f"Error al leer documento: {e}")
    
    async def update_document(
        self,
        database_name: str,
        container_name: str,
        doc_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actualiza un documento. El valor de partition key debe estar incluido en el documento
        según la ruta especificada en partition_key_path.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor
            doc_id (str): ID del documento
            data (Dict): Nuevos datos del documento (debe incluir el campo de partition key)
            
        Returns:
            Dict: Documento actualizado
            
        Example:
            # Si partition_key_path="/id"
            updated = await cosmos.update_document(
                "mi_app", "users", "user_123",
                {
                    "id": "user_123",
                    "name": "Juan Pérez Actualizado",
                    "age": 30
                }
            )
            
            # Si partition_key_path="/partition_key"
            updated = await cosmos.update_document(
                "mi_app", "users", "user_123",
                {
                    "id": "user_123",
                    "name": "Juan Pérez Actualizado",
                    "age": 30,
                    "partition_key": "user_123"
                }
            )
        """
        await self._ensure_initialized()
        
        try:
            container = await self._get_container(database_name, container_name)
            data["id"] = doc_id
            
            # Actualizar el documento
            result = await container.replace_item(
                item=doc_id,
                body=data
            )
            logger.info(f"Documento actualizado: {doc_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error al actualizar documento: {e}")
            raise CosmosDBError(f"Error al actualizar documento: {e}")
    
    async def delete_document(
        self,
        database_name: str,
        container_name: str,
        doc_id: str,
        partition_key: Optional[str] = None
    ) -> bool:
        """
        Elimina un documento.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor
            doc_id (str): ID del documento
            partition_key (str, optional): Clave de partición
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Example:
            # Eliminar documento
            deleted = await cosmos.delete_document("mi_app", "users", "user_123")
            if deleted:
                print("Usuario eliminado")
        """
        await self._ensure_initialized()
        
        try:
            container = await self._get_container(database_name, container_name)
            properties = await container.read()
            partition_key_paths = properties.get("partitionKey", {}).get("paths", [])
            if partition_key_paths:
                pk = partition_key if partition_key is not None else doc_id
                await container.delete_item(
                    item=doc_id,
                    partition_key=pk
                )
            else:
                await container.delete_item(
                    item=doc_id
                )
            logger.info(f"Documento eliminado: {doc_id}")
            return True
            
        except CosmosHttpResponseError as e:
            if e.status_code == 404:
                logger.warning(f"Documento no encontrado para eliminar: {doc_id}")
                return False
            raise CosmosDBError(f"Error al eliminar documento: {e.message}")
        except Exception as e:
            logger.error(f"Error al eliminar documento: {e}")
            raise CosmosDBError(f"Error al eliminar documento: {e}")
    
    async def query_documents(
        self,
        database_name: str,
        container_name: str,
        query: str,
        parameters: Optional[List[Dict[str, Any]]] = None,
        max_items: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor
            query (str): Consulta SQL
            parameters (List[Dict], optional): Parámetros de la consulta
            max_items (int): Número máximo de resultados
            
        Returns:
            List[Dict]: Lista de documentos que cumplen la consulta
            
        Example:
            # Consulta simple
            users = await cosmos.query_documents(
                "mi_app", "users",
                "SELECT * FROM c WHERE c.active = true"
            )
            
            # Consulta con parámetros
            users = await cosmos.query_documents(
                "mi_app", "users",
                "SELECT * FROM c WHERE c.age > @min_age",
                parameters=[{"name": "@min_age", "value": 18}]
            )
        """
        await self._ensure_initialized()
        
        try:
            container = await self._get_container(database_name, container_name)
            
            query_iterator = container.query_items(
                query=query,
                parameters=parameters or [],
                max_item_count=max_items
            )
            
            items = []
            async for item in query_iterator:
                items.append(item)
            
            logger.info(f"Consulta ejecutada: {len(items)} documentos encontrados")
            return items
            
        except Exception as e:
            logger.error(f"Error en consulta: {e}")
            raise CosmosDBError(f"Error al ejecutar consulta: {e}")
    
    # =============================================================================
    # OPERACIONES MASIVAS (BULK)
    # =============================================================================
    
    async def bulk_create_documents(
        self,
        database_name: str,
        container_name: str,
        documents: List[Dict[str, Any]],
        batch_size: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Crea múltiples documentos en lote.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor
            documents (List[Dict]): Lista de documentos a crear
            batch_size (int): Tamaño del lote
            
        Returns:
            List[Dict]: Documentos creados exitosamente
            
        Example:
            # Crear múltiples usuarios
            users = [
                {"name": "Juan", "email": "juan@example.com"},
                {"name": "María", "email": "maria@example.com"},
                {"name": "Pedro", "email": "pedro@example.com"}
            ]
            
            created = await cosmos.bulk_create_documents("mi_app", "users", users)
            print(f"Se crearon {len(created)} usuarios")
        """
        if not documents:
            return []
        
        created_docs = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_tasks = [
                self.create_document(database_name, container_name, doc)
                for doc in batch
            ]
            
            try:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if not isinstance(result, Exception):
                        created_docs.append(result)
                        
            except Exception as e:
                logger.error(f"Error en lote: {e}")
        
        logger.info(f"Operación bulk completada: {len(created_docs)} documentos creados")
        return created_docs
    
    async def bulk_read_documents(
        self,
        database_name: str,
        container_name: str,
        doc_ids: List[str],
        batch_size: int = 50
    ) -> List[Optional[Dict[str, Any]]]:
        """
        Lee múltiples documentos por sus IDs.
        
        Args:
            database_name (str): Nombre de la base de datos
            container_name (str): Nombre del contenedor
            doc_ids (List[str]): Lista de IDs de documentos
            batch_size (int): Tamaño del lote
            
        Returns:
            List[Optional[Dict]]: Lista de documentos (None si no existe)
            
        Example:
            # Leer múltiples usuarios
            user_ids = ["user_1", "user_2", "user_3"]
            users = await cosmos.bulk_read_documents("mi_app", "users", user_ids)
            
            for user in users:
                if user:
                    print(f"Usuario: {user['name']}")
                else:
                    print("Usuario no encontrado")
        """
        if not doc_ids:
            return []
        
        results = []
        
        for i in range(0, len(doc_ids), batch_size):
            batch_ids = doc_ids[i:i + batch_size]
            batch_tasks = [
                self.read_document(database_name, container_name, doc_id)
                for doc_id in batch_ids
            ]
            
            try:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.warning(f"Error leyendo documento: {result}")
                        results.append(None)
                    else:
                        results.append(result)
                        
            except Exception as e:
                logger.error(f"Error en lote de lectura: {e}")
                results.extend([None] * len(batch_ids))
        
        logger.info(f"Lectura bulk completada: {len([r for r in results if r is not None])} documentos encontrados")
        return results
    
    # =============================================================================
    # UTILIDADES INTERNAS
    # =============================================================================
    
    async def _get_container(self, database_name: str, container_name: str):
        """Obtiene o crea un contenedor."""
        cache_key = f"{database_name}/{container_name}"
        
        if cache_key not in self._container_cache:
            # Asegurar que la base de datos existe
            if database_name not in self._database_cache:
                database = await self.client.create_database_if_not_exists(id=database_name)
                self._database_cache[database_name] = database
            else:
                database = self._database_cache[database_name]
            
            # Obtener contenedor
            container = database.get_container_client(container_name)
            
            # Verificar que existe
            try:
                await container.read()
            except CosmosHttpResponseError as e:
                if e.status_code == 404:
                    raise CosmosDBError(f"Contenedor '{container_name}' no existe en base de datos '{database_name}'")
                raise
            
            self._container_cache[cache_key] = container
        
        return self._container_cache[cache_key]
    
    async def close(self):
        """Cierra el cliente y libera recursos."""
        if self.client:
            await self.client.close()
            logger.info("Cliente Cosmos DB cerrado")
    
    async def __aenter__(self):
        """Soporte para context manager."""
        await self._ensure_initialized()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup automático."""
        await self.close() 