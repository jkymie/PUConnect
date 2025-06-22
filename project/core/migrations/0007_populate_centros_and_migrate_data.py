# Generated manually

from django.db import migrations


def populate_centros(apps, schema_editor):
    Centro = apps.get_model('core', 'Centro')
    
    # Criar os centros baseados nas escolhas existentes
    centros_data = [
        ('ctch', 'Centro de Teologia e Ciências Humanas'),
        ('css', 'Centro de Ciências Sociais'),
        ('ctc', 'Centro Técnico Científico'),
        ('ccbs', 'Centro de Ciências Biológicas e da Saúde'),
    ]
    
    for codigo, nome in centros_data:
        Centro.objects.get_or_create(codigo=codigo, defaults={'nome': nome})


def migrate_centro_data(apps, schema_editor):
    Evento = apps.get_model('core', 'Evento')
    Centro = apps.get_model('core', 'Centro')
    
    # Para cada evento, adicionar o centro correspondente ao campo centros
    for evento in Evento.objects.all():
        if hasattr(evento, 'centro') and evento.centro:
            try:
                centro = Centro.objects.get(codigo=evento.centro)
                evento.centros.add(centro)
            except Centro.DoesNotExist:
                # Se o centro não existir, criar com o código
                centro = Centro.objects.create(codigo=evento.centro, nome=evento.centro)
                evento.centros.add(centro)


def reverse_migrate_centro_data(apps, schema_editor):
    # Não é necessário fazer nada no reverse
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_add_preco_info_and_multiple_centros'),
    ]

    operations = [
        # Popular a tabela Centro
        migrations.RunPython(populate_centros, reverse_migrate_centro_data),
        
        # Migrar dados do campo centro antigo para o novo relacionamento
        migrations.RunPython(migrate_centro_data, reverse_migrate_centro_data),
    ] 