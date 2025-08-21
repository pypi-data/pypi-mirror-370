import asyncio
import os
import json
from io import BytesIO, StringIO
from typing import Union, List, Optional
from datetime import datetime, timedelta

import pandas as pd
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

from dk_azure_services.common.config import AsyncConfigManager


class AsyncBlobStorage:
    """
    Cliente asíncrono para interactuar con Azure Blob Storage usando asyncio.to_thread.
    """

    def __init__(self):
        self.config_manager = AsyncConfigManager()
        self.account_name = None
        self.container_name = None
        self.account_key = None
        self.service_client = None
        self.container_client = None
        self._initialized = False
        self._lock = asyncio.Lock()

    async def _ensure_initialized(self):
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    await self._initialize()

    async def _initialize(self):
        cfg = await self.config_manager.get_blob_storage_config()
        self.account_name = cfg["account_name"]
        self.container_name = cfg["file_system_name"]
        self.account_key = cfg["account_key"]

        self.service_client = BlobServiceClient(
            account_url=f"https://{self.account_name}.blob.core.windows.net",
            credential=self.account_key
        )
        self.container_client = self.service_client.get_container_client(self.container_name)
        self._initialized = True

    # === Métodos públicos async ===

    async def list_blobs(self, prefix: Optional[str] = None, suffix: Optional[str] = None) -> List[str]:
        await self._ensure_initialized()
        return await asyncio.to_thread(self._list_blobs_sync, prefix, suffix)

    async def upload_data(self, blob_name: str, content: Union[str, dict, pd.DataFrame, bytes]) -> bool:
        await self._ensure_initialized()
        return await asyncio.to_thread(self._upload_data_sync, blob_name, content)

    async def download_blob(self, blob_name: str) -> bytes:
        await self._ensure_initialized()
        return await asyncio.to_thread(self._download_blob_sync, blob_name)

    async def delete_blob(self, blob_name: str) -> None:
        await self._ensure_initialized()
        await asyncio.to_thread(self._delete_blob_sync, blob_name)

    async def move_blob(self, src_blob: str, dest_blob: str) -> None:
        await self._ensure_initialized()
        await asyncio.to_thread(self._move_blob_sync, src_blob, dest_blob)

    async def generate_sas_for_blob(self, blob_name: str, permission_str: str = "r", expiry_hours: int = 1) -> Optional[str]:
        """
        Genera una URL SAS para un blob específico.
        
        Args:
            blob_name (str): Nombre del blob dentro del contenedor.
            permission_str (str): Permisos en formato string (ej: "r", "rw", "rwl").
            expiry_hours (int): Horas de validez del SAS.

        Returns:
            str | None: URL SAS o None si el blob no existe.
        """
        await self._ensure_initialized()

        # Verificar existencia
        blobs = await self.list_blobs(prefix=blob_name)
        if blob_name not in blobs:
            print(f"⚠ El blob '{blob_name}' no existe en el contenedor '{self.container_name}'.")
            return None

        expiry_time = datetime.utcnow() + timedelta(hours=expiry_hours)

        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=BlobSasPermissions.from_string(permission_str),
            expiry=expiry_time
        )

        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"

    
    async def upload_large_file(self, blob_name: str, file_path: str, chunk_size: int = 100 * 1024 * 1024):
        """Sube un archivo grande en chunks a Azure Blob Storage (asíncrono)."""
        await self._ensure_initialized()
        return await asyncio.to_thread(self._upload_large_file_sync, blob_name, file_path, chunk_size)

    # === Métodos internos sincrónicos ===
    
    def _upload_large_file_sync(self, blob_name: str, file_path: str, chunk_size: int = 100 * 1024 * 1024):
        """Versión síncrona para subir archivos grandes."""
        blob_client = self.container_client.get_blob_client(blob_name)
        file_size = os.path.getsize(file_path)

        print(f"📦 Subiendo '{file_path}' en chunks de {chunk_size / (1024*1024):.2f} MB "
              f"(tamaño total: {file_size / (1024*1024):.2f} MB)")

        with open(file_path, "rb") as file:
            block_ids = []
            idx = 0
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                block_id = str(idx).zfill(6)
                block_ids.append(block_id)
                blob_client.stage_block(block_id=block_id, data=chunk)
                idx += 1
                print(f"✅ Subido chunk {idx} ({len(chunk) / (1024*1024):.2f} MB)")

            blob_client.commit_block_list(block_ids)

        print("🎯 Subida completa")

    def _list_blobs_sync(self, prefix, suffix):
        blobs = self.container_client.list_blobs(name_starts_with=prefix)
        return [b.name for b in blobs if suffix is None or b.name.lower().endswith(suffix)]

    def _upload_data_sync(self, blob_name, content):
        blob_client = self.container_client.get_blob_client(blob_name)
        extension = blob_name.lower().split(".")[-1]

        if extension == "json":
            blob_client.upload_blob(json.dumps(content, ensure_ascii=False, indent=4), overwrite=True)
        elif extension == "csv":
            buffer = StringIO()
            content.to_csv(buffer, index=False)
            blob_client.upload_blob(buffer.getvalue(), overwrite=True)
        elif extension in ("xlsx", "xls"):
            buffer = BytesIO()
            content.to_excel(buffer, index=False)
            buffer.seek(0)
            blob_client.upload_blob(buffer.read(), overwrite=True)
        elif extension == "parquet":
            buffer = BytesIO()
            content.to_parquet(buffer, index=False)
            buffer.seek(0)
            blob_client.upload_blob(buffer.read(), overwrite=True)
        elif extension == "pdf":
            if not isinstance(content, (bytes, bytearray)):
                raise TypeError("Para PDF el contenido debe ser bytes.")
            blob_client.upload_blob(content, overwrite=True)
        else:
            blob_client.upload_blob(content, overwrite=True)
        return True

    def _download_blob_sync(self, blob_name):
        blob_client = self.container_client.get_blob_client(blob_name)
        return blob_client.download_blob().readall()

    def _delete_blob_sync(self, blob_name):
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.delete_blob()

    def _move_blob_sync(self, src_blob, dest_blob):
        source_blob = self.container_client.get_blob_client(src_blob)
        dest_client = self.container_client.get_blob_client(dest_blob)

        dest_client.start_copy_from_url(source_blob.url)
        source_blob.delete_blob()

    # === Context manager async ===
    async def __aenter__(self):
        await self._ensure_initialized()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
