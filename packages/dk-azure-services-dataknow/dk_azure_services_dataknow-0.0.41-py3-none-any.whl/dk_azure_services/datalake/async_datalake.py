import asyncio
import os
import json
from io import BytesIO, StringIO
from typing import Union, List, Dict, Any, Optional, BinaryIO

import pandas as pd
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobClient
from azure.storage.filedatalake import generate_file_system_sas, FileSystemSasPermissions
from datetime import datetime, timedelta

#from dk_azure_services.datalake.secrets import SecretManager

from dk_azure_services.common.config import AsyncConfigManager


class AsyncDataLake:
    def __init__(self):
        self.config_manager = AsyncConfigManager()
        self.account_name = None
        self.file_system_name = None
        self.account_key = None
        self.credential = None
        self.service_client = None
        self.file_system_client = None
        self._initialized = False
        self._lock = asyncio.Lock()

    async def _ensure_initialized(self):
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    await self._initialize()

    async def _initialize(self):
        # Obtener la configuración centralizada
        cfg = await self.config_manager.get_datalake_config()

        self.account_name = cfg["account_name"]
        self.file_system_name = cfg["file_system_name"]
        self.account_key = cfg["account_key"]

        self.credential = DefaultAzureCredential()
        self.service_client = DataLakeServiceClient(
            account_url=f"https://{self.account_name}.dfs.core.windows.net",
            credential=self.credential
        )
        self.file_system_client = self.service_client.get_file_system_client(self.file_system_name)
        self._initialized = True

    # === Métodos públicos async ===

    async def list_files(self, folder_path: str, suffix: Optional[str] = None) -> List[str]:
        await self._ensure_initialized()
        return await asyncio.to_thread(self._list_files_sync, folder_path, suffix)

    async def extract_files(self, folder_path: str, end: str) -> List[Dict[str, Any]]:
        await self._ensure_initialized()
        return await asyncio.to_thread(self._extract_files_sync, folder_path, end)

    async def save_data(self, folder_path: str, file_name: str, content: Union[str, dict, pd.DataFrame]) -> bool:
        await self._ensure_initialized()
        return await asyncio.to_thread(self._save_data_sync, folder_path, file_name, content)

    async def upload_file(self, file_name: str, dir_destiny: str, file_path: Optional[str] = None, file_obj: Optional[Union[bytes, BinaryIO]] = None) -> None:
        await self._ensure_initialized()
        await asyncio.to_thread(self._upload_file_sync, file_name, dir_destiny, file_path, file_obj)

    async def upload_large_file(self, file_name: str, file_path: str, chunk_size: int = 4 * 1024 * 1024):
        """
        Sube archivos grandes al Data Lake en chunks para manejar tamaños muy grandes (>4MB por bloque).

        Args:
            file_name (str): Ruta completa dentro del Data Lake (puede incluir carpeta, ej. 'carpeta/archivo.csv')
            file_path (str): Ruta local del archivo a subir.
            chunk_size (int): Tamaño de cada chunk en bytes (por defecto 4 MB).
        """
        await self._ensure_initialized()
        return await asyncio.to_thread(self._upload_large_file_sync, file_name, file_path, chunk_size)

    async def delete_file(self, file_path: str) -> None:
        await self._ensure_initialized()
        await asyncio.to_thread(self._delete_file_sync, file_path)

    async def move_file(self, src_path: str, dest_path: str) -> None:
        await self._ensure_initialized()
        await asyncio.to_thread(self._move_file_sync, src_path, dest_path)

    async def generate_sas_for_path(self, path: str, permission_str: str = "r", expiry_hours: int = 1) -> str:
        """
        Genera un SAS token para un archivo o carpeta en Azure Data Lake.
        """
        await self._ensure_initialized()

        # Obtener configuración del Data Lake
        cfg = await self.config_manager.get_datalake_config()
        account_name = cfg["account_name"]
        account_key = cfg["account_key"]

        expiry_time = datetime.utcnow() + timedelta(hours=expiry_hours)

        sas_token = generate_file_system_sas(
            account_name=account_name,
            file_system_name=self.file_system_name,
            file_path=path,
            credential=account_key,
            permission=FileSystemSasPermissions.from_string(permission_str),
            expiry=expiry_time
        )

        return f"https://{account_name}.dfs.core.windows.net/{self.file_system_name}/{path}?{sas_token}"


    # === Métodos internos sincrónicos ===

    def _list_files_sync(self, folder_path, suffix):
        paths = self.file_system_client.get_paths(path=folder_path)
        return [
            os.path.basename(p.name)
            for p in paths
            if not p.is_directory and (suffix is None or p.name.lower().endswith(suffix))
        ]

    def _extract_files_sync(self, folder_path, end):
        path_list = [path.name for path in self.file_system_client.get_paths(path=folder_path)]
        files_list = []
        for path_name in path_list:
            if path_name.lower().endswith(end):
                file_client = self.file_system_client.get_file_client(path_name)
                download = file_client.download_file()
                file_bytes = download.readall()
                files_list.append({
                    "file_name": path_name.split("/")[-1],
                    "file": file_bytes,
                })
        return files_list

    def _save_data_sync(self, folder_path, file_name, content):
        file_path = f"{folder_path}/{file_name}"
        extension = file_name.lower().split(".")[-1]
        file_client = self.file_system_client.get_file_client(file_path)

        if extension == "json":
            content_str = json.dumps(content, ensure_ascii=False, indent=4)
            file_client.upload_data(content_str, overwrite=True)
        elif extension == "csv":
            buffer = StringIO()
            content.to_csv(buffer, index=False)
            file_client.upload_data(buffer.getvalue(), overwrite=True)
        elif extension in ("xlsx", "xls"):
            buffer = BytesIO()
            content.to_excel(buffer, index=False)
            buffer.seek(0)
            file_client.upload_data(buffer.read(), overwrite=True)
        elif extension == "parquet":
            buffer = BytesIO()
            content.to_parquet(buffer, index=False)
            buffer.seek(0)
            file_client.upload_data(buffer.read(), overwrite=True)
        elif extension == "pdf":
            if not isinstance(content, (bytes, bytearray)):
                raise TypeError("Para PDF el contenido debe ser bytes.")
            file_client.upload_data(content, overwrite=True)
        else:
            file_client.upload_data(content, overwrite=True)
        return True

    def _upload_file_sync(self, file_name, dir_destiny, file_path=None, file_obj=None):
        file_full_path = os.path.join(dir_destiny, file_name)
        file_client = self.file_system_client.get_file_client(file_full_path)
        if file_obj is not None:
            file_client.upload_data(file_obj, overwrite=True)
        elif file_path is not None:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"El archivo local no existe: {file_path}")
            with open(file_path, "rb") as data:
                file_client.upload_data(data, overwrite=True)
        else:
            raise ValueError("Debe proporcionarse 'file_path' o 'file_obj'.")

    def _upload_large_file_sync(self, file_name: str, file_path: str, chunk_size: int):
        """
        Versión sincrónica para subir un archivo grande en chunks.
        """
        file_client = self.file_system_client.get_file_client(file_name)
        file_client.create_file()

        file_size = os.path.getsize(file_path)
        print(f"📦 Tamaño del archivo: {file_size / (1024*1024):.2f} MB")

        with open(file_path, "rb") as f:
            offset = 0
            while chunk := f.read(chunk_size):
                file_client.append_data(data=chunk, offset=offset, length=len(chunk))
                offset += len(chunk)

        file_client.flush_data(file_size)
        print(f"✅ Archivo grande '{file_name}' subido correctamente.")


    def _delete_file_sync(self, file_path):
        file_client = self.file_system_client.get_file_client(file_path)
        file_client.delete_file()

    def _move_file_sync(self, src_path, dest_path):
        blob_url = f"https://{self.file_system_client.account_name}.blob.core.windows.net"
        container_name = self.file_system_client.file_system_name
        credential = self.file_system_client.credential

        source_blob = BlobClient(blob_url, container_name=container_name, blob_name=src_path, credential=credential)
        destination_blob = BlobClient(blob_url, container_name=container_name, blob_name=dest_path, credential=credential)

        destination_blob.start_copy_from_url(source_blob.url)
        props = destination_blob.get_blob_properties()
        if props.copy.status != "success":
            raise RuntimeError(f"Fallo en la copia. Estado: {props.copy.status}")
        source_blob.delete_blob()

    # === Async context manager ===
    async def __aenter__(self):
        await self._ensure_initialized()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
