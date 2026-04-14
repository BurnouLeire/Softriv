# sales/services/supabase_storage.py - CORREGIDO
import logging
import uuid
from django.conf import settings
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    _client = None

    @classmethod
    def get_client(cls) -> Client:
        """Singleton del cliente Supabase"""
        if cls._client is None:
            supabase_url = settings.SUPABASE_URL
            supabase_key = settings.SUPABASE_KEY  # SERVICE_ROLE_KEY

            if not supabase_url or not supabase_key:
                raise ValueError("SUPABASE_URL y SUPABASE_KEY son requeridos")

            logger.info(f"Conectando a Supabase: {supabase_url}")
            cls._client = create_client(supabase_url, supabase_key)

        return cls._client

    @staticmethod
    def subir_pdf(contenido_bytes, nombre_base, bucket='test-public'):
        """
        Sube PDF directamente a Supabase Storage
        """
        try:
            client = SupabaseStorageService.get_client()

            # Limpiar nombre de archivo
            nombre_limpio = nombre_base.replace(' ', '_').replace('/', '-')
            nombre_archivo = f"cotizaciones/{uuid.uuid4()}_{nombre_limpio}.pdf"

            logger.info(
                f"Subiendo archivo: {nombre_archivo} al bucket: {bucket}")
            logger.info(f"Tamaño del archivo: {len(contenido_bytes)} bytes")

            # Subir archivo
            response = client.storage.from_(bucket).upload(
                path=nombre_archivo,
                file=contenido_bytes,
                file_options={
                    "content-type": "application/pdf",
                    "cache-control": "public, max-age=31536000",
                    "upsert": "true"
                }
            )

            logger.info(f"Respuesta de upload: {response}")

            # Obtener URL pública
            url_publica = client.storage.from_(
                bucket).get_public_url(nombre_archivo)

            logger.info(f"URL pública generada: {url_publica}")

            return url_publica

        except Exception as e:
            logger.error(f"Error subiendo a Supabase: {str(e)}", exc_info=True)
            raise Exception(f"Error en Supabase Storage: {str(e)}")
