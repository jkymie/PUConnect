from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Evento, SolicitarOrganizador, UserProfile

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    matricula = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    curso = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipo_usuario = forms.ChoiceField(
        choices=[('aluno', 'Aluno'), ('organizador', 'Organizador de Eventos')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cpf = forms.CharField(max_length=14, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'matricula', 'curso', 'telefone', 'tipo_usuario', 'cpf', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        matricula = cleaned_data.get('matricula')
        curso = cleaned_data.get('curso')

        if tipo_usuario == 'aluno':
            if not matricula:
                self.add_error('matricula', 'Matrícula é obrigatória para alunos')
            if not curso:
                self.add_error('curso', 'Curso é obrigatório para alunos')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.matricula = self.cleaned_data['matricula']
        user.curso = self.cleaned_data['curso']
        user.telefone = self.cleaned_data.get('telefone')
        user.tipo_usuario = self.cleaned_data.get('tipo_usuario')
        user.cpf = self.cleaned_data.get('cpf')
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
        fields = ['bio', 'foto', 'curso', 'matricula', 'data_nascimento', 'telefone']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        } 