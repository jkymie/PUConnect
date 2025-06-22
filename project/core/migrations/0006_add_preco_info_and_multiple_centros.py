# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_evento_centro_evento_horas_complementares_and_more'),
    ]

    operations = [
        # Adicionar campo preco_info ao Evento
        migrations.AddField(
            model_name='evento',
            name='preco_info',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Valor inicial que o usuário terá que pagar para participar do evento',
                max_digits=10,
                null=True,
                verbose_name='valor inicial'
            ),
        ),
        
        # Criar modelo Centro
        migrations.CreateModel(
            name='Centro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=10, unique=True, verbose_name='código')),
                ('nome', models.CharField(max_length=100, verbose_name='nome')),
            ],
            options={
                'verbose_name': 'centro',
                'verbose_name_plural': 'centros',
                'ordering': ['nome'],
            },
        ),
        
        # Adicionar campo centros como ManyToManyField
        migrations.AddField(
            model_name='evento',
            name='centros',
            field=models.ManyToManyField(
                help_text='Selecione um ou mais centros para este evento',
                to='core.centro',
                verbose_name='centros'
            ),
        ),
    ] 