from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    matricula = forms.CharField(max_length=20, required=True)
    curso = forms.CharField(max_length=100, required=True)
    telefone = forms.CharField(max_length=20, required=False)
    tipo_usuario = forms.ChoiceField(choices=User.TIPO_USUARIO_CHOICES, required=True)
    cpf = forms.CharField(max_length=14, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'matricula', 'curso', 'telefone', 'tipo_usuario', 'cpf', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
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