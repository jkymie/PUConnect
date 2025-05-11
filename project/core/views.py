from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm

def index(request):
    return render(request, 'core/index.html')

def inscricoes(request):
    return render(request, 'core/inscricoes.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
        messages.error(request, 'Unsuccessful registration. Invalid information.')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
        messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def home(request):
    return render(request, 'core/home.html')

 