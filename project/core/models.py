from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    vagas = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
    
    def vagas_disponiveis(self):
        """Retorna o número de vagas disponíveis no evento"""
        inscritos = self.inscricoes.count()
        return max(0, self.vagas - inscritos)
    
    def tem_vagas_disponiveis(self):
        """Verifica se o evento ainda tem vagas disponíveis"""
        return self.vagas_disponiveis() > 0
    
    def verificar_inscricao(self, usuario):
        """Verifica se um usuário está inscrito no evento"""
        return self.inscricoes.filter(usuario=usuario).exists()
    
    @property
    def esta_inscrito(self):
        """Propriedade que verifica se o usuário atual está inscrito no evento"""
        from django.contrib.auth.models import AnonymousUser
        if not hasattr(self, '_current_user'):
            return False
        if isinstance(self._current_user, AnonymousUser):
            return False
        return self.inscricoes.filter(usuario=self._current_user).exists()

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

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    foto = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    curso = models.CharField(max_length=100, blank=True)
    matricula = models.CharField(max_length=20, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f'Perfil de {self.user.username}'
    
    def get_eventos_participados(self):
        return Evento.objects.filter(inscricoes__usuario=self.user).order_by('-data_hora')
    
    def get_eventos_organizados(self):
        return Evento.objects.filter(organizador=self.user).order_by('-data_hora')
    
    def get_total_eventos_participados(self):
        return self.user.inscricoes.count()
    
    def get_total_eventos_organizados(self):
        return Evento.objects.filter(organizador=self.user).count()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
