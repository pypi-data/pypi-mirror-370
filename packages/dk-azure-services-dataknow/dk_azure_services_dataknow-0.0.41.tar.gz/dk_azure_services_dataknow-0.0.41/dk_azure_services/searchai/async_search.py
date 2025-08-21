import asyncio
from typing import Optional, Dict, List, Any

# Clientes asincrónicos de Azure Cognitive Search
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.models import SearchIndex, SearchField

# Autenticación
from azure.core.credentials import AzureKeyCredential

# Config manager centralizado
from dk_azure_services.common.config import AsyncConfigManager


class AsyncSearchEngine:
    def __init__(self):
        # Configuración desde Key Vault o .env
        self.config_manager = AsyncConfigManager()
        self.endpoint = None
        self.api_key = None
        self.index_name = None
        self.credential = None
        self.search_client = None
        self.index_client = None
        self._initialized = False
        self._lock = asyncio.Lock()

    async def _ensure_initialized(self):
        """Asegura que el cliente esté inicializado antes de usarlo."""
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    await self._initialize()

    async def _initialize(self):
        """Carga configuración y crea clientes de Azure Search."""
        cfg = await self.config_manager.get_search_config()  
        self.endpoint = cfg["endpoint"]
        self.api_key = cfg["api_key"]
        self.index_name = cfg["index_name"]

        # Usamos la API Key como credencial
        self.credential = AzureKeyCredential(self.api_key)

        self.index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=self.credential
        )
        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credential
        )

        self._initialized = True

    # === OPERACIONES DE ÍNDICE ===
    async def create_index(self, index_name: str, fields: List[SearchField]):
        await self._ensure_initialized()
        index = SearchIndex(name=index_name, fields=fields)
        await self.index_client.create_index(index)

    async def delete_index(self, index_name: str):
        await self._ensure_initialized()
        await self.index_client.delete_index(index_name)

    async def list_indexes(self) -> List[str]:
        await self._ensure_initialized()
        indexes = []
        async for idx in self.index_client.list_indexes():
            indexes.append(idx.name)
        return indexes



    # === OPERACIONES DE DOCUMENTOS ===
    async def upload_documents(self, documents: List[Dict[str, Any]]):
        await self._ensure_initialized()
        return await self.search_client.upload_documents(documents)

    async def search(self, query: str, top: int = 5, filters: Optional[str] = None) -> List[Dict[str, Any]]:
        await self._ensure_initialized()
        results = await self.search_client.search(
            search_text=query,
            filter=filters,
            top=top
        )
        return [doc async for doc in results]

    async def get_document(self, key: str) -> Dict[str, Any]:
        await self._ensure_initialized()
        return await self.search_client.get_document(key=key)

    async def delete_documents(self, documents: List[Dict[str, Any]]):
        await self._ensure_initialized()
        return await self.search_client.delete_documents(documents)

    # === CIERRE Y CONTEXTO ASYNC ===
    async def close(self):
        if self.index_client:
            await self.index_client.close()
        if self.search_client:
            await self.search_client.close()

    async def __aenter__(self):
        await self._ensure_initialized()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
