"""
Módulo simplificado para Azure Cosmos DB.

Una sola importación, máxima simplicidad, mínima configuración.

Uso básico:
    from dk_azure_services.cosmos import AsyncCosmosDBClient
    
    async with AsyncCosmosDBClient() as cosmos:
        # Crear base de datos
        await cosmos.create_database("mi_app")
        
        # Crear contenedor
        await cosmos.create_container("mi_app", "users", "/user_id")
        
        # Crear documento
        await cosmos.create_document("mi_app", "users", {
            "id": "user_123",
            "name": "Juan Pérez",
            "email": "juan@example.com"
        })
        
        # Consultar documentos
        users = await cosmos.query_documents(
            "mi_app", "users",
            "SELECT * FROM c WHERE c.active = true"
        )

Para casos avanzados, también están disponibles los clientes especializados:
    from dk_azure_services.cosmos import (
        AsyncDatabaseManager,        # Solo gestión de bases de datos
        AsyncContainerManager,       # Solo gestión de contenedores
        AsyncDocumentsManager          # Solo operaciones de documentos
    )
"""

# 🌟 CLIENTE PRINCIPAL (RECOMENDADO)
from .simple_client import AsyncCosmosDBClient

# 🔧 CLIENTES ESPECIALIZADOS (Para casos avanzados)
from .documents_manager import AsyncDocumentsManager
from .database_manager import AsyncDatabaseManager
from .container_manager import AsyncContainerManager, ContainerConfig

# 📝 EXPORTACIONES PRINCIPALES
__all__ = [
    # 🌟 Cliente Principal (MÁXIMA SIMPLICIDAD)
    "AsyncCosmosDBClient",           # Cliente simplificado - RECOMENDADO
    
    # 🔧 Clientes Especializados (Para casos avanzados)
    "AsyncDatabaseManager",          # Gestión especializada de bases de datos
    "AsyncContainerManager",         # Gestión especializada de contenedores
    "AsyncDocumentsManager",         # Operaciones especializadas de documentos
    
    # 🛠️ Utilidades Avanzadas
    "ContainerConfig"                # Configuración avanzada de contenedores
]

# Información del módulo
__version__ = "2.0.0"
__author__ = "DK Azure Services Team"
__description__ = "Cliente simplificado para Azure Cosmos DB - Máxima simplicidad, mínima configuración" 