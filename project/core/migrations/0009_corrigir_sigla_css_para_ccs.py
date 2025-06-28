# Generated manually

from django.db import migrations


def corrigir_sigla_css_para_ccs(apps, schema_editor):
    Centro = apps.get_model('core', 'Centro')
    
    # Atualizar o centro CSS para CCS
    try:
        centro_css = Centro.objects.get(codigo='css')
        centro_css.codigo = 'ccs'
        centro_css.save()
        print("Sigla CSS corrigida para CCS")
    except Centro.DoesNotExist:
        print("Centro CSS não encontrado")


def reverse_corrigir_sigla(apps, schema_editor):
    Centro = apps.get_model('core', 'Centro')
    
    # Reverter a correção (voltar para CSS)
    try:
        centro_ccs = Centro.objects.get(codigo='ccs')
        centro_ccs.codigo = 'css'
        centro_ccs.save()
        print("Sigla CCS revertida para CSS")
    except Centro.DoesNotExist:
        print("Centro CCS não encontrado")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_old_centro_field'),
    ]

    operations = [
        migrations.RunPython(corrigir_sigla_css_para_ccs, reverse_corrigir_sigla),
    ] 