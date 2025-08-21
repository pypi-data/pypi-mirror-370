# DK Azure Services Package

Paquete Python para facilitar la integración con servicios de Azure, proporcionando conectores seguros y fáciles de usar para los principales servicios de Azure.

## Servicios Soportados

- **Azure Cosmos DB** - Base de datos NoSQL distribuida globalmente
- **Azure Cognitive Search** - Búsqueda semántica y texto completo
- **Azure Data Lake Storage Gen2** - Data Lake para analítica a escala
- **Azure Blob Storage** - Almacenamiento de objetos en la nube
- **Azure Key Vault** - Gestión segura de secretos y certificados
- **Azure OpenAI** - Servicios de inteligencia artificial (próximamente)

## Características Principales

✅ **Autenticación Centralizada** - Usa `DefaultAzureCredential` para autenticación segura  
✅ **Configuración por Entornos** - Soporte para múltiples entornos (dev, prod, etc.)  
✅ **Gestión de Secretos** - Integración automática con Azure Key Vault  
✅ **Manejo de Errores** - Excepciones personalizadas para mejor debugging  
✅ **Documentación Completa** - Docstrings en español  
✅ **Type Hints** - Compatibilidad completa con tipado estático  
🚀 **100% Asíncrono** - Operaciones concurrentes de alto rendimiento por defecto  
⚡ **Operaciones Bulk** - Procesamiento masivo optimizado (10-50x más rápido)  
🔧 **Context Managers** - Gestión automática de recursos  
🎯 **API Simple** - Una sola forma de hacer las cosas, bien hecha  

## Instalación

```bash
pip install dk-azure-services
```

### Instalación para Desarrollo

```bash
git clone https://github.com/yourusername/dk-azure-services.git
cd dk-azure-services
pip install -e .[dev]
```

## Uso Rápido

### Cliente Simplificado (AsyncCosmosDBClient)

```python
import asyncio
from dk_azure_services.cosmos import AsyncCosmosDBClient
from dotenv import load_dotenv

# Requieres tu archivo .env con la variable de entorno: KEY_VAULT_NAME=your-key-vault-name
# En tu Key Vault requieres los secretos:
# cosmos-uri="your-cosmos-uri"
# cosmos-key=your-cosmos-key


load_dotenv(override=True)

async def main():
    async with AsyncCosmosDBClient(partition_key_path="/partition_key") as client:
        # Crear una base de datos
        await client.create_database("mi_base_de_datos")

        # Crear un contenedor
        await client.create_container("mi_base_de_datos", "mi_contenedor", "/partition_key")

        # Crear un documento
        documento = {"id": "user123", "name": "Juan", "role": "Developer", "partition_key": "user123"}
        await client.create_document("mi_base_de_datos", "mi_contenedor", documento)

        # Leer un documento
        doc = await client.read_document("mi_base_de_datos", "mi_contenedor", "user123", partition_key="user123")
        print("Documento leído:", doc)

asyncio.run(main())
```

### Azure Data Lake (AsyncDataLake)

```python
import asyncio
from dk_azure_services import AsyncDataLake
from dotenv import load_dotenv

load_dotenv(override=True)

async def main():
    async with AsyncDataLake() as dl:
        # Listar archivos CSV en una carpeta
        files = await dl.list_files("datos/", suffix=".csv")
        print(files)

        # Subir archivo grande en chunks
        await dl.upload_large_file(
            file_name="datos/grande.csv",
            file_path="./local_grande.csv",
            chunk_size=4 * 1024 * 1024
        )

        # Generar SAS para un path
        sas_url = await dl.generate_sas_for_path("datos/grande.csv", permission_str="r", expiry_hours=2)
        print("SAS:", sas_url)

asyncio.run(main())
```

### Azure Blob Storage (AsyncBlobStorage)

```python
import asyncio
from dk_azure_services import AsyncBlobStorage
from dotenv import load_dotenv

load_dotenv(override=True)

async def main():
    async with AsyncBlobStorage() as storage:
        # Subir JSON
        await storage.upload_data("ejemplos/demo.json", {"ok": True})

        # Listar blobs por prefijo
        blobs = await storage.list_blobs(prefix="ejemplos/")
        print(blobs)

        # Generar SAS de lectura por 1 hora
        url = await storage.generate_sas_for_blob("ejemplos/demo.json", permission_str="r", expiry_hours=1)
        print("URL SAS:", url)

asyncio.run(main())
```

### Azure Cognitive Search (AsyncSearchEngine)

```python
import asyncio
from dk_azure_services import AsyncSearchEngine
from dotenv import load_dotenv

load_dotenv(override=True)

async def main():
    async with AsyncSearchEngine() as search:
        # Subir documentos
        await search.upload_documents([
            {"id": "1", "title": "Hola", "content": "Documento de prueba"},
            {"id": "2", "title": "Mundo", "content": "Otro documento"}
        ])

        # Buscar
        results = await search.search("prueba", top=3)
        print(results)

asyncio.run(main())
```

---

## Ejemplo Avanzado: Clientes Especializados

Puedes usar clientes especializados para un control más granular sobre bases de datos, contenedores y documentos.

```python
import asyncio
from dk_azure_services.cosmos.database_manager import AsyncDatabaseManager
from dk_azure_services.cosmos.container_manager import AsyncContainerManager
from dk_azure_services.cosmos.documents_manager import AsyncDocumentsManager

async def main():
    # Crear base de datos
    db_manager = AsyncDatabaseManager(environment="dev")
    await db_manager.create_database("ejemplo_db")

    # Crear contenedor
    container_manager = AsyncContainerManager(environment="dev")
    await container_manager.create_container_simple(
        database_name="ejemplo_db",
        container_name="ejemplo_contenedor",
        partition_key_path="/partition_key"
    )

    # Crear documento
    client = AsyncDocumentsManager(environment="dev")
    doc = {"id": "user1", "nombre": "Ana", "edad": 28, "partition_key": "user1"}
    await client.create_document(doc, "ejemplo_db", "ejemplo_contenedor", partition_key="user1")

    # Consultar documentos
    docs = await client.query_documents(
        "SELECT * FROM c WHERE c.edad >= @edad",
        [{"name": "@edad", "value": 18}],
        database_name="ejemplo_db",
        container_name="ejemplo_contenedor"
    )
    print("Documentos encontrados:", docs)

    # Cerrar conexiones
    await client.close()
    await container_manager.close()
    await db_manager.close()

asyncio.run(main())
```

> **Nota:** Puedes encontrar ejemplos completos y scripts de prueba en la carpeta `examples/02_cosmos` del repositorio.

---

## Configuración

### 🎯 **Variables Estandarizadas Entre Ambientes**

✅ **Mismos nombres** en DEV y PROD  
✅ **Solo cambian** valores y Key Vault  
✅ **Deployment simplificado**

El paquete busca la configuración en este orden:

1. **Variables de entorno** (ej: `COSMOS_URI`)
2. **Azure Key Vault** (ej: `cosmos-uri`)
3. **Valor por defecto**

### Variables de Entorno (Desarrollo Local)

#### Configuración Estándar:
```bash
# Variables sin prefijo de ambiente
COSMOS_URI=https://your-cosmos-dev.documents.azure.com:443/
COSMOS_KEY=your-cosmos-dev-key
COSMOS_DATABASE=myapp-dev
COSMOS_CONTAINER=documents
COSMOS_PARTITION=/id

# Configuración del entorno
APP_ENV=dev
KEY_VAULT_NAME=your-keyvault-dev

# Azure Data Lake
DATALAKE_ACCOUNT_NAME=your-adls-account
DATALAKE_FILE_SYSTEM_NAME=your-filesystem
DATALAKE_ACCOUNT_KEY=your-adls-key

# Azure Blob Storage
BLOB_STORAGE_ACCOUNT_NAME=your-blob-account
BLOB_STORAGE_FILE_SYSTEM_NAME=your-container
BLOB_STORAGE_ACCOUNT_KEY=your-blob-key

# Azure Cognitive Search
SEARCH_ENDPOINT=https://your-search-service.search.windows.net
SEARCH_API_KEY=your-search-api-key
SEARCH_INDEX_NAME=your-index
```

### Azure Key Vault (Producción)

#### Secretos por Ambiente:

**DESARROLLO** - Key Vault: `your-keyvault-dev`
- `cosmos-uri`
- `cosmos-key`
- `cosmos-database`
- `cosmos-container`
- `datalake-account-name`
- `datalake-file-system-name`
- `datalake-account-key`
- `blob-storage-account-name`
- `blob-storage-file-system-name`
- `blob-storage-account-key`
- `search-endpoint`
- `search-api-key`
- `search-index-name`

**PRODUCCIÓN** - Key Vault: `your-keyvault-prod`
- `cosmos-uri` (mismos nombres!)
- `cosmos-key`
- `cosmos-database`
- `cosmos-container`
- `datalake-account-name`
- `datalake-file-system-name`
- `datalake-account-key`
- `blob-storage-account-name`
- `blob-storage-file-system-name`
- `blob-storage-account-key`
- `search-endpoint`
- `search-api-key`
- `search-index-name`

> 🔄 **Para cambiar ambiente**: Solo actualiza `KEY_VAULT_NAME=your-keyvault-prod`

## Autenticación con Azure

El paquete utiliza `DefaultAzureCredential` que soporta múltiples métodos:

- ✅ Azure CLI (`az login`)
- ✅ Visual Studio Code
- ✅ Managed Identity (en Azure)
- ✅ Variables de entorno
- ✅ Interactive browser

### Configurar Azure CLI (Recomendado para desarrollo)

```bash
az login
```

## Estructura del Proyecto

```
dk_azure_services/
├── __init__.py              # Exportaciones principales
├── common/                  # Utilidades compartidas
│   ├── auth.py             # Autenticación centralizada
│   ├── config.py           # Gestión de configuración
│   └── exceptions.py       # Excepciones personalizadas
├── cosmos/                  # Azure Cosmos DB
│   ├── __init__.py
│   ├── simple_client.py    # Cliente simplificado principal
│   ├── database_manager.py # Gestión de bases de datos (avanzado)
│   ├── container_manager.py# Gestión de contenedores (avanzado)
│   └── documents_manager.py# Gestión de documentos (avanzado)
├── datalake/                # Azure Data Lake Storage Gen2
│   └── async_datalake.py
├── blob_storage/            # Azure Blob Storage
│   └── async_blob_storage.py
├── searchai/                # Azure Cognitive Search
│   └── async_search.py
└── keyvault/               # Azure Key Vault (gestión vía common/config)
```

## Ejemplos Avanzados

### Uso con ConfigManager Personalizado

```python
from dk_azure_services.common.config import ConfigManager
from dk_azure_services import CosmosDBClient

# Configuración personalizada
config = ConfigManager(environment="production", key_vault_name="my-vault")
client = CosmosDBClient(config_manager=config)
```

### Operaciones en Lote

```python
# Crear múltiples documentos
documentos = [
    {"id": "user1", "name": "Ana", "role": "Manager"},
    {"id": "user2", "name": "Carlos", "role": "Developer"},
    {"id": "user3", "name": "María", "role": "Designer"}
]

resultados = client.bulk_create_documents(documentos)
print(f"Creados {len(resultados)} documentos")
```

### Información del Contenedor

```python
info = client.get_container_info()
print(f"Entorno: {info['environment']}")
print(f"Base de datos: {info['database_name']}")
print(f"Contenedor: {info['container_name']}")
```

## Desarrollo

### Configurar Entorno de Desarrollo

```bash
# Clonar el repositorio
git clone https://github.com/yourusername/dk-azure-services.git
cd dk-azure-services

# Instalar dependencias de desarrollo
pip install -e .[dev]

# Configurar pre-commit hooks
pre-commit install
```

### Ejecutar Tests

```bash
pytest
```

### Formatear Código

```bash
black dk_azure_services/
isort dk_azure_services/
```

### Verificar Tipado

```bash
mypy dk_azure_services/
```

## ¿Por qué 100% Asíncrono? 🤔

Este paquete fue diseñado desde cero para ser **completamente asíncrono** por estas razones:

### **🎯 Rendimiento Superior**
- **10-50x más rápido** para operaciones en lote
- **Concurrencia nativa** - múltiples operaciones simultáneas
- **Eficiencia de recursos** - menos uso de CPU y memoria

### **🚀 Ideal para Servicios de Azure**
- **Azure Cosmos DB** - Base de datos distribuida (I/O intensivo)
- **Azure OpenAI** - Llamadas a LLMs con alta latencia
- **Azure Blob Storage** - Transferencia de archivos grandes
- **Azure Key Vault** - Operaciones de red para secretos

### **📱 Perfecto para Apps Modernas**
- **FastAPI** - Framework asíncrono por excelencia  
- **Starlette** - Base asíncrona sólida
- **Microservicios** - Escalabilidad superior
- **APIs REST** - Mejor throughput

### **🧠 API Más Simple**
- **Una sola forma** de hacer las cosas (bien hecha)
- **Context managers** automáticos
- **Menos decisiones** que tomar al desarrollar

> 💡 **Tip**: Si necesitas compatibilidad síncrona, puedes usar `asyncio.run()` o bibliotecas como `asgiref.sync.sync_to_async()`.

## Roadmap

- [x] Azure Cosmos DB - Cliente asíncrono completo
- [x] Azure Data Lake - Cliente asíncrono
- [x] Azure Blob Storage - Cliente asíncrono
- [x] Azure Cognitive Search - Cliente asíncrono
- [ ] Azure OpenAI - Cliente para chat y embeddings
- [ ] Azure Key Vault - Cliente extendido
- [ ] Azure Service Bus - Mensajería
- [ ] Ejemplos con FastAPI
- [ ] Template de Docker
- [ ] CI/CD con GitHub Actions

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una branch para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'feat: add amazing feature'`)
4. Push a la branch (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Autor

**Leonar Santiago Castro** - *Desarrollo inicial* - [GitHub](https://github.com/yourusername)

## Agradecimientos

- Equipo de Azure SDK para Python
- Comunidad de desarrolladores de Azure
- Contribuidores del proyecto 