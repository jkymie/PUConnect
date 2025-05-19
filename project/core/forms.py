from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .models import User, Evento, SolicitarOrganizador, UserProfile

class UserRegistrationForm(UserCreationForm):
    tipo_usuario = forms.ChoiceField(
        choices=[('aluno', 'Aluno'), ('organizador', 'Organizador de Eventos')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_('Tipo de Usuário')
    )

    matricula = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua matrícula'
        }),
        label=_('Matrícula')
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label=_('E-mail')
    )

    class Meta:
        model = User
        fields = ('username', 'tipo_usuario', 'matricula', 'email', 'password1', 'password2')
        labels = {
            'username': _('Nome de usuário'),
            'password1': _('Senha'),
            'password2': _('Confirmação de senha'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['tipo_usuario']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.matricula = self.cleaned_data['matricula']
        user.tipo_usuario = self.cleaned_data.get('tipo_usuario')
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class EventoForm(forms.ModelForm):
    titulo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    descricao = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )
    data_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    local = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    vagas = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Evento
        fields = ['titulo', 'descricao', 'data_hora', 'local', 'vagas']
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'titulo': _('Título'),
            'descricao': _('Descrição'),
            'data_hora': _('Data e Hora'),
            'local': _('Local'),
            'vagas': _('Número de Vagas'),
        }

class SolicitarOrganizadorForm(forms.ModelForm):
    class Meta:
        model = SolicitarOrganizador
        fields = ['motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Explique por que você gostaria de se tornar um organizador de eventos...'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'foto', 'data_nascimento']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Conte um pouco sobre você...'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'bio': _('Biografia'),
            'foto': _('Foto de perfil'),
            'data_nascimento': _('Data de nascimento'),
        } 