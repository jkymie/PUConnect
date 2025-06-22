from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

# Modelos principais do sistema de eventos e usuários customizados

class User(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ('aluno', 'Aluno'),
        ('organizador', 'Organizador de Eventos'),
    ]

    #e-mail é obrigatório e único para cada usuário
    email = models.EmailField(_('email address'), unique=True)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='aluno',
        verbose_name=_('tipo de usuário')
    )

    #matrícula é o identificador principal do usuário
    matricula = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('matrícula')
    )

    #telefone é opcional, mas segue o padrão brasileiro
    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\(\d{2}\) \d{5}-\d{4}$',
                message='Telefone deve estar no formato (XX) XXXXX-XXXX'
            )
        ],
        verbose_name=_('telefone')
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        ordering = ['-date_joined']

    def __str__(self):
        return self.matricula

    def clean(self):
        super().clean()
        if not self.matricula:
            raise ValidationError({'matricula': 'Matrícula é obrigatória para todos os usuários'})

class Evento(models.Model):
    PRICE_CHOICES = [
        ('gratuito', 'Gratuito'),
        ('pago', 'Pago'),
    ]
    PLACE_CHOICES = [
        ('puc', 'PUC'),
        ('fora', 'Fora da PUC'),
    ]
    EVENT_TYPE_CHOICES = [
        ('online', 'Online'),
        ('presencial', 'Presencial'),
    ]
    DEPARTMENT_CHOICES = [
        ('ctch', 'Centro de Teologia e Ciências Humanas'),
        ('css', 'Centro de Ciências Sociais'),
        ('ctc', 'Centro Técnico Científico'),
        ('ccbs', 'Centro de Ciências Biológicas e da Saúde'),
    ]

    titulo = models.CharField(max_length=200, verbose_name=_('título'))
    descricao = models.TextField(verbose_name=_('descrição'))
    data_hora = models.DateTimeField(verbose_name=_('data e hora'))
    local = models.CharField(max_length=200, verbose_name=_('local'))
    vagas = models.PositiveIntegerField(default=0, verbose_name=_('vagas'))
    preco = models.CharField(max_length=10, choices=PRICE_CHOICES, default='gratuito', verbose_name=_('preço'))
    preco_info = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name=_('valor inicial'),
        help_text=_('Valor inicial que o usuário terá que pagar para participar do evento')
    )
    lugar = models.CharField(max_length=10, choices=PLACE_CHOICES, default='puc', verbose_name=_('lugar'))
    tipo_evento = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES, default='presencial', verbose_name=_('tipo de evento'))
    centros = models.ManyToManyField(
        'Centro',
        verbose_name=_('centros'),
        help_text=_('Selecione um ou mais centros para este evento')
    )
    horas_complementares = models.BooleanField(default=False, verbose_name=_('horas complementares'))
    imagem = models.ImageField(upload_to='eventos/', null=True, blank=True, verbose_name=_('imagem'))
    organizador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo_usuario': 'organizador'},
        verbose_name=_('organizador')
    )
    inscritos = models.ManyToManyField(User, through='Inscricao', related_name='eventos_inscritos')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name=_('criado em'))

    class Meta:
        verbose_name = _('evento')
        verbose_name_plural = _('eventos')
        ordering = ['-data_hora']

    def __str__(self):
        return self.titulo
    
    def clean(self):
        super().clean()
        # Não deixa criar evento no passado
        if self.data_hora and self.data_hora < timezone.now():
            raise ValidationError({'data_hora': 'A data e hora do evento não podem ser no passado.'})
        
        # Validação para preço_info quando o evento é pago
        if self.preco == 'pago' and (self.preco_info is None or self.preco_info <= 0):
            raise ValidationError({'preco_info': 'Para eventos pagos, é necessário informar um valor inicial maior que zero.'})
        
        # Validação para preço_info quando o evento é gratuito
        if self.preco == 'gratuito' and self.preco_info and self.preco_info > 0:
            raise ValidationError({'preco_info': 'Para eventos gratuitos, o valor inicial deve ser zero ou não informado.'})
    
    def vagas_disponiveis(self):
        """Retorna quantas vagas ainda estão disponíveis para o evento."""
        inscritos = self.inscricoes.count()
        return max(0, self.vagas - inscritos)
    
    def tem_vagas_disponiveis(self):
        """True se ainda há vagas para o evento."""
        return self.vagas_disponiveis() > 0
    
    def esta_lotado(self):
        """True se o evento está lotado mas ainda vai acontecer."""
        return not self.tem_vagas_disponiveis() and self.get_proximidade_temporal() != 'encerrado'
    
    def esta_inscrito(self, usuario):
        """Verifica se o usuário já está inscrito neste evento."""
        return self.inscricoes.filter(usuario=usuario).exists()
    
    def get_proximidade_temporal(self):
        """Retorna a proximidade temporal do evento (hoje, amanhã, essa semana, esse mês, encerrado)."""
        try:
            from datetime import date
            hoje = date.today()
            data_evento = self.data_hora.date()
            if data_evento < hoje:
                return 'encerrado'
            if data_evento == hoje:
                return 'hoje'
            elif data_evento == hoje + timedelta(days=1):
                return 'amanha'
            elif data_evento <= hoje + timedelta(days=7):
                return 'semana'
            elif data_evento.month == hoje.month and data_evento.year == hoje.year:
                return 'mes'
            else:
                return None
        except Exception as e:
            print(f"Erro no get_proximidade_temporal: {e}")
            return None

class Inscricao(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='inscricoes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscricoes')
    data_inscricao = models.DateTimeField(auto_now_add=True)
    presente = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('inscrição')
        verbose_name_plural = _('inscrições')
        unique_together = ['evento', 'usuario']
        ordering = ['-data_inscricao']

    def __str__(self):
        return f'{self.usuario.username} - {self.evento.titulo}'

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
    bio = models.TextField(max_length=500, blank=True, verbose_name=_('biografia'))
    foto = models.ImageField(upload_to='profile_photos/', null=True, blank=True, verbose_name=_('foto'))
    data_nascimento = models.DateField(null=True, blank=True, verbose_name=_('data de nascimento'))
    curso = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('curso'))
    
    class Meta:
        verbose_name = _('perfil')
        verbose_name_plural = _('perfis')

    def __str__(self):
        return f'Perfil de {self.user.username}'
    
    def get_eventos_participados(self):
        # Retorna todos os eventos em que o usuário está inscrito
        return Evento.objects.filter(inscricoes__usuario=self.user).order_by('-data_hora')
    
    def get_eventos_organizados(self):
        # Retorna todos os eventos organizados por este usuário
        return Evento.objects.filter(organizador=self.user).order_by('-data_hora')
    
    def get_total_eventos_participados(self):
        return self.user.inscricoes.count()
    
    def get_total_eventos_organizados(self):
        return Evento.objects.filter(organizador=self.user).count()

class Centro(models.Model):
    codigo = models.CharField(max_length=10, unique=True, verbose_name=_('código'))
    nome = models.CharField(max_length=100, verbose_name=_('nome'))
    
    class Meta:
        verbose_name = _('centro')
        verbose_name_plural = _('centros')
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
