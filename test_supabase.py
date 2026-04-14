# test_supabase_fixed.py
"""
Test de Supabase Storage usando TU .env real
Ejecutar: python test_supabase_fixed.py
"""

import uuid
import os
import sys
from pathlib import Path

# Forzar la ruta del .env
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / '.env'

print("=" * 60)
print("🔍 TEST DE SUPABASE STORAGE (CON TU .ENV)")
print("=" * 60)
print(f"\n📁 Buscando .env en: {ENV_PATH}")
print(f"   ¿Existe? {ENV_PATH.exists()}")

if not ENV_PATH.exists():
    print("\n❌ Archivo .env NO ENCONTRADO")
    sys.exit(1)

# Cargar .env manualmente
print("\n📖 Cargando variables del .env...")
env_vars = {}
with open(ENV_PATH, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            env_vars[key] = value
            os.environ[key] = value

print(f"   Variables cargadas: {len(env_vars)}")

# Verificar variables clave con TUS NOMBRES REALES
# ← Tu variable se llama SUPABASE_URL
SUPABASE_URL = env_vars.get('SUPABASE_URL')
# ← Tu variable se llama SUPABASE_SERVICE_ROLE_KEY
SUPABASE_KEY = env_vars.get('SUPABASE_SERVICE_ROLE_KEY')
SUPABASE_ANON_KEY = env_vars.get('SUPABASE_KEY')  # ← Esta es la ANON_KEY

print(f"\n📌 SUPABASE_URL: {SUPABASE_URL}")
print(
    f"📌 SUPABASE_SERVICE_ROLE_KEY: {SUPABASE_KEY[:30] if SUPABASE_KEY else 'NO ENCONTRADA'}...")
print(
    f"📌 SUPABASE_KEY (ANON): {SUPABASE_ANON_KEY[:30] if SUPABASE_ANON_KEY else 'NO ENCONTRADA'}...")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n❌ Faltan variables requeridas")
    print("   SUPABASE_URL:", "✅" if SUPABASE_URL else "❌")
    print("   SUPABASE_SERVICE_ROLE_KEY:", "✅" if SUPABASE_KEY else "❌")
    sys.exit(1)

# Probar conexión
print("\n🔄 Conectando a Supabase...")
try:
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Cliente creado")
except ImportError:
    print("❌ Supabase no instalado. Ejecuta: pip install supabase")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Listar buckets
print("\n📦 Buckets disponibles:")
try:
    buckets = client.storage.list_buckets()
    if buckets:
        for b in buckets:
            print(f"   - {b.name} (público: {b.public})")
    else:
        print("   (ninguno)")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Solución: Crea el bucket en Supabase Studio")
    print(f"   {SUPABASE_URL} → Storage → New Bucket → test-public")
    sys.exit(1)

# Verificar test-public
bucket_existe = any(b.name == 'test-public' for b in buckets)
if not bucket_existe:
    print("\n⚠️  Bucket 'test-public' no existe. Creando...")
    try:
        client.storage.create_bucket('test-public', options={'public': True})
        print("✅ Bucket 'test-public' creado")
        buckets = client.storage.list_buckets()
    except Exception as e:
        print(f"❌ No se pudo crear: {e}")
        print("\nCrealo manualmente en Supabase Studio:")
        print(f"   {SUPABASE_URL}")
        print("   Storage → New Bucket → Nombre: test-public → Public: ON")
        sys.exit(1)

# Probar subida
print("\n📤 Probando subida a 'test-public'...")
test_file = f"test/test_{uuid.uuid4().hex[:8]}.txt"
test_content = b"Test desde Django - " + uuid.uuid4().hex.encode()

try:
    result = client.storage.from_('test-public').upload(
        test_file,
        test_content,
        file_options={"content-type": "text/plain", "upsert": "true"}
    )
    print(f"✅ Subido: {test_file}")

    url = client.storage.from_('test-public').get_public_url(test_file)
    print(f"\n🔗 URL: {url}")

    # Verificar acceso HTTP
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read()
            print(f"✅ URL accesible (HTTP {resp.status})")
            print(f"   Contenido: {content.decode()[:50]}...")
    except urllib.error.HTTPError as e:
        print(f"⚠️  HTTP Error {e.code}: {e.reason}")
        print("   Verifica las políticas RLS del bucket")
    except Exception as e:
        print(f"⚠️  No se pudo acceder: {e}")

except Exception as e:
    print(f"❌ Error subiendo: {e}")
    print("\nPosible solución: Políticas RLS")
    print("Ejecuta en Supabase Studio → SQL Editor:")
    print("""
    -- Dar permisos públicos al bucket
    CREATE POLICY "Public Access test-public" 
    ON storage.objects FOR SELECT 
    USING (bucket_id = 'test-public');
    
    CREATE POLICY "Public Upload test-public" 
    ON storage.objects FOR INSERT 
    WITH CHECK (bucket_id = 'test-public');
    
    CREATE POLICY "Public Update test-public" 
    ON storage.objects FOR UPDATE 
    USING (bucket_id = 'test-public');
    """)

print("\n" + "=" * 60)
print("✅ TEST COMPLETADO")
print("=" * 60)
