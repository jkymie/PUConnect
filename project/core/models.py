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

class Inscricao(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='inscricoes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscricoes')
    data_inscricao = models.DateTimeField(auto_now_add=True)
    presente = models.BooleanField(default=False)

    class Meta:
        unique_together = ('evento', 'usuario')
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'

    def __str__(self):
        return f"{self.usuario.username} - {self.evento.titulo}"

class SolicitarOrganizador(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitacoes_organizador')
    motivo = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_resposta = models.DateTimeField(null=True, blank=True)
    resposta = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Solicitação de Organizador'
        verbose_name_plural = 'Solicitações de Organizador'
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"Solicitação de {self.usuario.username} - {self.status}"
