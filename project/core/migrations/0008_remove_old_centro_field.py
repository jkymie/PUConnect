# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_populate_centros_and_migrate_data'),
    ]

    operations = [
        # Remover o campo centro antigo
        migrations.RemoveField(
            model_name='evento',
            name='centro',
        ),
    ] 