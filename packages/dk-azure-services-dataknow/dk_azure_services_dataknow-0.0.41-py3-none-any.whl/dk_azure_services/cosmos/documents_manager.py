"""
Cliente asíncrono para Azure Cosmos DB optimizado para operaciones concurrentes.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, AsyncIterator
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.core import MatchConditions

from ..common.config import AsyncConfigManager
from ..common.auth import AsyncAzureAuthenticator
from ..common.exceptions import CosmosDBError, ConfigurationError

logger = logging.getLogger(__name__)


class AsyncDocumentsManager:
    """
    Cliente asíncrono para Azure Cosmos DB con configuración segura por entorno.
    
    Optimizado para operaciones concurrentes y de alto rendimiento.
    Utiliza el sistema de configuración centralizada asíncrono para obtener credenciales
    desde variables de entorno o Azure Key Vault de forma automática.
    
    Soporta tanto configuración fija desde Key Vault como parámetros dinámicos
    para base de datos y contenedor.
    """
    
    def __init__(self, environment: str = None, config_manager: AsyncConfigManager = None):
        """
        Inicializa el cliente asíncrono para Cosmos DB con configuración segura por entorno.
        
        Args:
            environment (str, optional): Entorno de ejecución (dev, prod, etc.)
            config_manager (AsyncConfigManager, optional): Administrador de configuración personalizado
        """
        self.environment = environment or "dev"
        self.config_manager = config_manager or AsyncConfigManager(self.environment)
        
        # Variables para inicialización lazy
        self.config = None
        self.client = None
        self.database = None
        self.container = None
        self._initialized = False
        self._lock = asyncio.Lock()
        
        # Cache para bases de datos y contenedores dinámicos
        self._database_cache = {}
        self._container_cache = {}
        
        logger.info(f"Cliente asíncrono Cosmos DB creado para entorno: {self.environment}")
    
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
        Inicializa el cliente y los recursos de manera asíncrona.
        """
        try:
            # Cargar configuración
            self.config = await self.config_manager.get_cosmos_config()
            
            # Inicializar cliente Cosmos
            self.client = CosmosClient(self.config["uri"], self.config["key"])
            
            # Inicializar base de datos y contenedor por defecto
            # self.database = await self.client.create_database_if_not_exists(id=self.config["database_name"])
            # self.container = await self.database.create_container_if_not_exists(
            #     id=self.config["container_name"],
            #     partition_key=PartitionKey(path=self.config["partition_key"])
            # )
            
            self._initialized = True
            logger.info(f"Cliente asíncrono Cosmos DB inicializado para entorno: {self.environment}")
        except Exception as e:
            logger.error(f"Error al inicializar cliente asíncrono Cosmos DB: {e}")
            raise CosmosDBError(f"Fallo en la inicialización: {e}")
    
    async def _get_database_and_container(self, database_name: str = None, container_name: str = None, partition_key: str = None):
        """
        Obtiene o crea la base de datos y contenedor especificados.
        
        Args:
            database_name (str, optional): Nombre de la base de datos
            container_name (str, optional): Nombre del contenedor
            partition_key (str, optional): Clave de partición para el contenedor
            
        Returns:
            tuple: (database, container) - Referencias a la base de datos y contenedor
        """
        await self._ensure_initialized()
        
        # Si no se especifican, usar configuración por defecto
        if not database_name and not container_name:
            return self.database, self.container
        
        # Obtener o crear base de datos
        if database_name:
            if database_name not in self._database_cache:
                self._database_cache[database_name] = await self.client.create_database_if_not_exists(id=database_name)
            database = self._database_cache[database_name]
        else:
            database = self.database
        
        # Obtener o crear contenedor
        if container_name:
            cache_key = f"{database_name or 'default'}:{container_name}"
            if cache_key not in self._container_cache:
                # Usar partition_key proporcionado o el de configuración por defecto
                pk_path = partition_key or self.config["partition_key"]
                self._container_cache[cache_key] = await database.create_container_if_not_exists(
                    id=container_name,
                    partition_key=PartitionKey(path=pk_path)
                )
            container = self._container_cache[cache_key]
        else:
            container = self.container
        
        return database, container
    
    async def create_document(
        self, 
        data: Dict[str, Any], 
        database_name: str = None, 
        container_name: str = None,
        partition_key: str = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo documento en el contenedor especificado de manera asíncrona.
        
        Args:
            data (Dict[str, Any]): Datos del documento a crear
            database_name (str, optional): Nombre de la base de datos. Si no se especifica, usa la configuración por defecto
            container_name (str, optional): Nombre del contenedor. Si no se especifica, usa la configuración por defecto
            partition_key (str, optional): Clave de partición para el contenedor. Si no se especifica, usa la configuración por defecto
            
        Returns:
            Dict[str, Any]: Documento creado exitosamente
        """
        database, container = await self._get_database_and_container(database_name, container_name, partition_key)
        
        if "id" not in data:
            data["id"] = str(uuid.uuid4())
        
        try:
            result = await container.create_item(body=data)
            logger.info(f"Documento creado asíncronamente con ID: {result['id']} en {database_name or 'default'}/{container_name or 'default'}")
            return result
        except CosmosHttpResponseError as e:
            logger.error(f"Error al crear documento asíncrono: {e}")
            raise CosmosDBError(f"Error al crear documento asíncrono: {e.message}", status_code=e.status_code)
    
    async def read_document_by_id(
        self, 
        doc_id: str, 
        partition_key: str = None,
        database_name: str = None, 
        container_name: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Lee un documento por su ID de manera asíncrona.
        
        Args:
            doc_id (str): ID del documento
            partition_key (str, optional): Clave de partición. Si no se proporciona, se asume igual al ID
            database_name (str, optional): Nombre de la base de datos. Si no se especifica, usa la configuración por defecto
            container_name (str, optional): Nombre del contenedor. Si no se especifica, usa la configuración por defecto
            
        Returns:
            Dict[str, Any] or None: Documento encontrado o None si no existe
            
        Raises:
            CosmosDBError: Si ocurre un error distinto a "no encontrado"
        """
        database, container = await self._get_database_and_container(database_name, container_name)
        
        try:
            # Para contenedores sin partition key, usar None
            # Para contenedores con partition key, usar el valor proporcionado
            pk_value = None
            if partition_key:
                pk_value = [partition_key] if isinstance(partition_key, str) else partition_key
            
            document = await container.read_item(
                item=doc_id, 
                partition_key=pk_value  
            )
            logger.info(f"Documento leído asíncronamente: {doc_id} desde {database_name or 'default'}/{container_name or 'default'}")
            return document
        except CosmosHttpResponseError as e:
            if e.status_code == 404:
                logger.warning(f"Documento no encontrado: {doc_id}")
                return None
            logger.error(f"Error al leer documento asíncrono: {e}")
            raise CosmosDBError(
                f"Error al leer documento asíncrono '{doc_id}': {e.message}",
                status_code=e.status_code
            )
    
    async def query_documents(
        self, 
        query: str, 
        parameters: List[Dict[str, Any]] = None, 
        max_item_count: int = 100,
        database_name: str = None, 
        container_name: str = None
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta personalizada sobre los documentos de manera asíncrona.
        
        Args:
            query (str): Consulta SQL a ejecutar
            parameters (List[Dict[str, Any]], optional): Parámetros de la consulta
            max_item_count (int): Número máximo de documentos a retornar
            database_name (str, optional): Nombre de la base de datos. Si no se especifica, usa la configuración por defecto
            container_name (str, optional): Nombre del contenedor. Si no se especifica, usa la configuración por defecto
            
        Returns:
            List[Dict[str, Any]]: Lista de documentos que cumplen la consulta
            
        Raises:
            CosmosDBError: Si ocurre un error al ejecutar la consulta
        """
        database, container = await self._get_database_and_container(database_name, container_name)
        
        try:
            # Obtener el iterador asíncrono
            query_iterator = container.query_items(
                query=query,
                parameters=parameters or [],
                max_item_count=max_item_count
            )
            
            # Recolectar todos los elementos de manera asíncrona
            items = []
            async for item in query_iterator:
                items.append(item)
            
            logger.info(f"Consulta asíncrona ejecutada: {len(items)} documentos encontrados en {database_name or 'default'}/{container_name or 'default'}")
            return items
        except CosmosHttpResponseError as e:
            logger.error(f"Error en consulta asíncrona: {e}")
            raise CosmosDBError(
                f"Error al ejecutar consulta asíncrona: {e.message}",
                status_code=e.status_code
            )
    
    async def query_documents_stream(
        self, 
        query: str, 
        parameters: List[Dict[str, Any]] = None, 
        max_item_count: int = 100,
        database_name: str = None, 
        container_name: str = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Ejecuta una consulta personalizada y retorna un stream asíncrono de documentos.
        
        Args:
            query (str): Consulta SQL a ejecutar
            parameters (List[Dict[str, Any]], optional): Parámetros de la consulta
            max_item_count (int): Número máximo de documentos por lote
            database_name (str, optional): Nombre de la base de datos. Si no se especifica, usa la configuración por defecto
            container_name (str, optional): Nombre del contenedor. Si no se especifica, usa la configuración por defecto
            
        Yields:
            Dict[str, Any]: Documento individual del resultado
            
        Raises:
            CosmosDBError: Si ocurre un error al ejecutar la consulta
        """
        database, container = await self._get_database_and_container(database_name, container_name)
        
        try:
            query_iterator = container.query_items(
                query=query,
                parameters=parameters or [],
                max_item_count=max_item_count
            )
            
            count = 0
            async for item in query_iterator:
                yield item
                count += 1
            
            logger.info(f"Stream de consulta asíncrona completado: {count} documentos procesados en {database_name or 'default'}/{container_name or 'default'}")
        except CosmosHttpResponseError as e:
            logger.error(f"Error en stream de consulta asíncrona: {e}")
            raise CosmosDBError(
                f"Error en stream de consulta asíncrona: {e.message}",
                status_code=e.status_code
            )
    
    async def update_document(
        self, 
        doc_id: str, 
        data: Dict[str, Any], 
        etag: str, 
        partition_key: str = None,
        database_name: str = None, 
        container_name: str = None
    ) -> Dict[str, Any]:
        """
        Actualiza un documento existente usando control de concurrencia (etag) de manera asíncrona.
        
        Args:
            doc_id (str): ID del documento
            data (Dict[str, Any]): Nuevos datos del documento
            etag (str): ETag del documento para validación de concurrencia
            partition_key (str, optional): Clave de partición
            database_name (str, optional): Nombre de la base de datos. Si no se especifica, usa la configuración por defecto
            container_name (str, optional): Nombre del contenedor. Si no se especifica, usa la configuración por defecto
            
        Returns:
            Dict[str, Any]: Documento actualizado
            
        Raises:
            CosmosDBError: Si ocurre un error al actualizar el documento
        """
        database, container = await self._get_database_and_container(database_name, container_name)
        
        try:
            # Para contenedores sin partition key, usar None
            # Para contenedores con partition key, usar el valor proporcionado
            pk_value = None
            if partition_key:
                pk_value = [partition_key] if isinstance(partition_key, str) else partition_key
            
            updated_doc = await container.replace_item(
                item=doc_id,
                body=data,
                etag=etag,
                match_condition=MatchConditions.IfNotModified,
                # partition_key=pk_value
            )
            logger.info(f"Documento actualizado asíncronamente: {doc_id} en {database_name or 'default'}/{container_name or 'default'}")
            return updated_doc
        except CosmosHttpResponseError as e:
            logger.error(f"Error al actualizar documento asíncrono: {e}")
            if e.status_code == 412:
                raise CosmosDBError(
                    f"El documento '{doc_id}' fue modificado por otro proceso (conflicto de concurrencia)",
                    status_code=e.status_code
                )
            raise CosmosDBError(
                f"Error al actualizar documento asíncrono '{doc_id}': {e.message}",
                status_code=e.status_code
            )
    
    async def delete_document(
        self, 
        doc_id: str, 
        partition_key: str = None,
        database_name: str = None, 
        container_name: str = None
    ) -> bool:
        """
        Elimina un documento del contenedor de manera asíncrona.
        
        Args:
            doc_id (str): ID del documento a eliminar
            partition_key (str, optional): Clave de partición
            database_name (str, optional): Nombre de la base de datos. Si no se especifica, usa la configuración por defecto
            container_name (str, optional): Nombre del contenedor. Si no se especifica, usa la configuración por defecto
            
        Returns:
            bool: True si el documento fue eliminado exitosamente
            
        Raises:
            CosmosDBError: Si ocurre un error al eliminar el documento
        """
        database, container = await self._get_database_and_container(database_name, container_name)
        
        try:
            # Para contenedores sin partition key, usar None
            # Para contenedores con partition key, usar el valor proporcionado
            pk_value = None
            if partition_key:
                pk_value = [partition_key] if isinstance(partition_key, str) else partition_key
            
            await container.delete_item(
                item=doc_id,
                partition_key=pk_value
            )
            logger.info(f"Documento eliminado asíncronamente: {doc_id} desde {database_name or 'default'}/{container_name or 'default'}")
            return True
        except CosmosHttpResponseError as e:
            logger.error(f"Error al eliminar documento asíncrono: {e}")
            if e.status_code == 404:
                logger.warning(f"Documento no encontrado para eliminar: {doc_id}")
                return False
            raise CosmosDBError(
                f"Error al eliminar documento asíncrono '{doc_id}': {e.message}",
                status_code=e.status_code
            )
    
    async def bulk_create_documents(
        self, 
        documents: List[Dict[str, Any]], 
        batch_size: int = 25,
        database_name: str = None, 
        container_name: str = None,
        partition_key: str = None
    ) -> List[Dict[str, Any]]:
        """
        Crea múltiples documentos en paralelo optimizado para máximo rendimiento.
        
        Args:
            documents (List[Dict[str, Any]]): Lista de documentos a crear
            batch_size (int): Tamaño del lote para procesamiento paralelo
            database_name (str, optional): Nombre de la base de datos. Si no se especifica, usa la configuración por defecto
            container_name (str, optional): Nombre del contenedor. Si no se especifica, usa la configuración por defecto
            partition_key (str, optional): Clave de partición para el contenedor. Si no se especifica, usa la configuración por defecto
            
        Returns:
            List[Dict[str, Any]]: Lista de documentos creados exitosamente
        """
        if not documents:
            return []
        
        created_docs = []
        
        # Procesar en lotes para optimizar performance
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_tasks = [
                self.create_document(doc, database_name, container_name, partition_key) 
                for doc in batch
            ]
            
            try:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if not isinstance(result, Exception):
                        created_docs.append(result)
                        
            except Exception as e:
                logger.error(f"Error crítico en lote: {e}")
        
        logger.info(f"Operación bulk asíncrona completada: {len(created_docs)} documentos creados de {len(documents)} en {database_name or 'default'}/{container_name or 'default'}")
        return created_docs
    
    async def bulk_read_documents(
        self, 
        doc_ids: List[str], 
        batch_size: int = 50,
        database_name: str = None, 
        container_name: str = None
    ) -> List[Optional[Dict[str, Any]]]:
        """
        Lee múltiples documentos en paralelo por sus IDs.
        
        Args:
            doc_ids (List[str]): Lista de IDs de documentos a leer
            batch_size (int): Tamaño del lote para procesamiento paralelo
            database_name (str, optional): Nombre de la base de datos. Si no se especifica, usa la configuración por defecto
            container_name (str, optional): Nombre del contenedor. Si no se especifica, usa la configuración por defecto
            
        Returns:
            List[Optional[Dict[str, Any]]]: Lista de documentos (None si no existe)
        """
        if not doc_ids:
            return []
        
        results = []
        
        # Procesar en lotes
        for i in range(0, len(doc_ids), batch_size):
            batch_ids = doc_ids[i:i + batch_size]
            batch_tasks = [
                self.read_document_by_id(doc_id, database_name=database_name, container_name=container_name) 
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
                logger.error(f"Error crítico en lote de lectura: {e}")
                # Añadir None para cada documento del lote fallido
                results.extend([None] * len(batch_ids))
        
        logger.info(f"Lectura bulk asíncrona completada: {len([r for r in results if r is not None])} documentos encontrados de {len(doc_ids)} en {database_name or 'default'}/{container_name or 'default'}")
        return results
    
    async def get_container_info(self, database_name: str = None, container_name: str = None) -> Dict[str, Any]:
        """
        Obtiene información del contenedor especificado de manera asíncrona.
        
        Args:
            database_name (str, optional): Nombre de la base de datos. Si no se especifica, usa la configuración por defecto
            container_name (str, optional): Nombre del contenedor. Si no se especifica, usa la configuración por defecto
            
        Returns:
            Dict[str, Any]: Información del contenedor y configuración
        """
        database, container = await self._get_database_and_container(database_name, container_name)
        
        return {
            "environment": self.environment,
            "database_name": database.id,
            "container_name": container.id,
            "partition_key": self.config["partition_key"],
            "cosmos_endpoint": self.config["uri"].split("//")[1].split(".")[0] if "//" in self.config["uri"] else "unknown",
            "client_type": "async",
            "is_dynamic": database_name is not None or container_name is not None
        }
    
    async def close(self):
        """
        Cierra el cliente y libera todos los recursos de manera segura.
        
        Asegura que todas las sesiones HTTP y conexiones se cierren correctamente
        para evitar warnings de 'Unclosed client session'.
        """
        try:
            # Cerrar config manager primero
            if self.config_manager:
                await self.config_manager.close()
                
            # Cerrar cliente principal con manejo de excepciones
            if self.client:
                try:
                    # Dar tiempo para que operaciones pendientes terminen
                    await asyncio.sleep(0.1)
                    
                    # Cerrar cliente Cosmos DB
                    await self.client.close()
                    
                    # Dar tiempo adicional para que las conexiones se cierren limpiamente
                    await asyncio.sleep(0.2)
                    
                    logger.info("Cliente asíncrono Cosmos DB cerrado correctamente")
                    
                except Exception as e:
                    logger.warning(f"Advertencia al cerrar cliente Cosmos DB: {e}")
                finally:
                    self.client = None
                    
            # Limpiar referencias
            self.database = None
            self.container = None
            self.config = None
            self._initialized = False
            
        except Exception as e:
            logger.error(f"Error durante el cierre del cliente: {e}")
        
        # Forzar garbage collection para limpiar sesiones residuales
        import gc
        gc.collect()
        
        # Esperar final para asegurar cierre completo
        await asyncio.sleep(0.1)
    
    async def __aenter__(self):
        """
        Soporte para context manager asíncrono.
        """
        await self._ensure_initialized()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Limpieza automática al salir del context manager.
        """
        await self.close() 