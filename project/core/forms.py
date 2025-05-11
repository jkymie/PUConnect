from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    matricula = forms.CharField(max_length=20, required=True)
    curso = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'matricula', 'curso', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.matricula = self.cleaned_data['matricula']
        user.curso = self.cleaned_data['curso']
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'})) 