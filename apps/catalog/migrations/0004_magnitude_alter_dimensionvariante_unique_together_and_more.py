from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_remove_servicios_catalog_ser_cod_fac_0bab01_idx_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Magnitud',
            new_name='Magnitude',
        ),
    ]