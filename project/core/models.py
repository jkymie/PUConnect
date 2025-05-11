from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    matricula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    curso = models.CharField(max_length=100, null=True, blank=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    TIPO_USUARIO_CHOICES = [
        ('aluno', 'Aluno'),
        ('admin', 'Administrador'),
        ('organizador', 'Organizador de Eventos'),
    ]
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='aluno')
    cpf = models.CharField(max_length=14, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    data_hora = models.DateTimeField()
    local = models.CharField(max_length=200)
    organizador = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'organizador'})
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
