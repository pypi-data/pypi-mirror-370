"""
Excepciones personalizadas para el paquete dk_azure_services.
"""


class AzureServiceError(Exception):
    """
    Excepción base para errores relacionados con servicios de Azure.
    """
    def __init__(self, message, service_name=None, error_code=None):
        """
        Inicializa la excepción con información detallada del error.
        
        Args:
            message (str): Mensaje descriptivo del error
            service_name (str, optional): Nombre del servicio Azure que causó el error
            error_code (str, optional): Código de error específico del servicio
        """
        self.message = message
        self.service_name = service_name
        self.error_code = error_code
        super().__init__(self.message)
    
    def __str__(self):
        """
        Representación en string del error con información adicional.
        """
        error_parts = [self.message]
        if self.service_name:
            error_parts.append(f"Servicio: {self.service_name}")
        if self.error_code:
            error_parts.append(f"Código: {self.error_code}")
        return " | ".join(error_parts)


class ConfigurationError(AzureServiceError):
    """
    Excepción para errores de configuración.
    """
    def __init__(self, message, missing_config=None):
        """
        Inicializa el error de configuración.
        
        Args:
            message (str): Mensaje descriptivo del error
            missing_config (str, optional): Nombre de la configuración faltante
        """
        self.missing_config = missing_config
        super().__init__(message, service_name="Configuration")


class AuthenticationError(AzureServiceError):
    """
    Excepción para errores de autenticación con Azure.
    """
    def __init__(self, message):
        """
        Inicializa el error de autenticación.
        
        Args:
            message (str): Mensaje descriptivo del error
        """
        super().__init__(message, service_name="Authentication")


class CosmosDBError(AzureServiceError):
    """
    Excepción específica para errores de Azure Cosmos DB.
    """
    def __init__(self, message, status_code=None):
        """
        Inicializa el error de Cosmos DB.
        
        Args:
            message (str): Mensaje descriptivo del error
            status_code (int, optional): Código de estado HTTP del error
        """
        self.status_code = status_code
        super().__init__(message, service_name="Cosmos DB", error_code=str(status_code) if status_code else None)


class OpenAIError(AzureServiceError):
    """
    Excepción específica para errores de Azure OpenAI.
    """
    def __init__(self, message, model_name=None):
        """
        Inicializa el error de OpenAI.
        
        Args:
            message (str): Mensaje descriptivo del error
            model_name (str, optional): Nombre del modelo que causó el error
        """
        self.model_name = model_name
        super().__init__(message, service_name="OpenAI")


class BlobStorageError(AzureServiceError):
    """
    Excepción específica para errores de Azure Blob Storage.
    """
    def __init__(self, message, container_name=None, blob_name=None):
        """
        Inicializa el error de Blob Storage.
        
        Args:
            message (str): Mensaje descriptivo del error
            container_name (str, optional): Nombre del contenedor
            blob_name (str, optional): Nombre del blob
        """
        self.container_name = container_name
        self.blob_name = blob_name
        super().__init__(message, service_name="Blob Storage")


class KeyVaultError(AzureServiceError):
    """
    Excepción específica para errores de Azure Key Vault.
    """
    def __init__(self, message, secret_name=None):
        """
        Inicializa el error de Key Vault.
        
        Args:
            message (str): Mensaje descriptivo del error
            secret_name (str, optional): Nombre del secreto que causó el error
        """
        self.secret_name = secret_name
        super().__init__(message, service_name="Key Vault") 