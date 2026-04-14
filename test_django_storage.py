# test_django_storage.py
import os
import sys
import uuid
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings

print("=" * 60)
print("🔍 TEST DE DJANGO-STORAGES CON SUPABASE S3")
print("=" * 60)

# Ver configuración
print(f"\n📌 AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}")
print(f"📌 AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
print(f"📌 DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")

# Probar subida
test_file = f"test/test_{uuid.uuid4().hex[:8]}.txt"
test_content = b"Test desde Django Storage - " + uuid.uuid4().hex.encode()

print(f"\n📤 Subiendo archivo: {test_file}")
try:
    # Guardar
    path = default_storage.save(test_file, ContentFile(test_content))
    print(f"✅ Archivo guardado, ruta: {path}")
    
    # Obtener URL
    url = default_storage.url(path)
    print(f"🔗 URL: {url}")
    
    # Verificar acceso HTTP
    import urllib.request
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            content = resp.read()
            print(f"✅ URL accesible (HTTP {resp.status})")
            print(f"   Contenido: {content.decode()[:50]}...")
    except Exception as e:
        print(f"⚠️ No se pudo acceder a la URL: {e}")
    
    # Verificar que existe
    exists = default_storage.exists(path)
    print(f"📁 ¿Existe en storage? {exists}")
    
    # Eliminar archivo de prueba
    default_storage.delete(path)
    print(f"🗑️ Archivo de prueba eliminado")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ TEST COMPLETADO")
print("=" * 60)