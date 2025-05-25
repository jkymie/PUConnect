from django.db import migrations, models

def forward_func(apps, schema_editor):
    User = apps.get_model('core', 'User')
    for user in User.objects.all():
        if not user.matricula:
            # If user has CPF, use it as matricula
            if user.cpf:
                user.matricula = user.cpf.replace('.', '').replace('-', '')
            else:
                # If no CPF, use username as matricula
                user.matricula = user.username
            user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # First, make matricula required but allow null temporarily
        migrations.AlterField(
            model_name='user',
            name='matricula',
            field=models.CharField(max_length=20, unique=True, null=True, verbose_name='matrícula'),
        ),
        # Run the data migration
        migrations.RunPython(forward_func),
        # Then make matricula non-nullable
        migrations.AlterField(
            model_name='user',
            name='matricula',
            field=models.CharField(max_length=20, unique=True, verbose_name='matrícula'),
        ),
        # Finally, remove the CPF field
        migrations.RemoveField(
            model_name='user',
            name='cpf',
        ),
    ] 