# sales/services/file_manager.py
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import uuid

class GestorArchivosService:

    @staticmethod
    def guardar_proforma_pdf(contenido_bytes, nombre_base):
        """
        Guarda el PDF en el sistema de archivos (local o S3 según DEFAULT_FILE_STORAGE)
        """
        # Limpiar nombre de archivo
        nombre_archivo = f"proformas/{uuid.uuid4()}_{nombre_base}.pdf"
        
        # Guardar usando el Storage de Django (respeta MEDIA_ROOT o S3 Boto3)
        ruta = default_storage.save(nombre_archivo, ContentFile(contenido_bytes))
        
        # Devolver la URL pública o relativa
        return default_storage.url(ruta)