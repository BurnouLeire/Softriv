from django.db import migrations

GRUPOS = [
    "Administrador",
    "Vendedor",
    "Tecnico",
    "Digitador",
    "Calidad",
    "Gerencia",
    "Coordinador OT",
]

def crear_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for nombre in GRUPOS:
        Group.objects.get_or_create(name=nombre)

def eliminar_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=GRUPOS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_user_rol_delete_usuariorol'),
    ]

    operations = [
        migrations.RunPython(crear_grupos, eliminar_grupos),
    ]