from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from .forms import UserRegistrationForm, UserLoginForm, EventoForm, UserProfileForm, EmailChangeForm
from .models import Evento, Inscricao, UserProfile
from django.contrib.auth.forms import PasswordChangeForm

def index(request):
    return render(request, 'core/index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'core.backends.MatriculaBackend'
            auth_login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('index')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Login realizado com sucesso!')
                return redirect('index')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = UserLoginForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('index')

def is_organizador(user):
    return user.is_authenticated and user.tipo_usuario == 'organizador'

@login_required
@user_passes_test(is_organizador)
def evento_create(request):
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user
            evento.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('meus-eventos')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = EventoForm()
    return render(request, 'core/evento_form.html', {'form': form, 'action': 'Criar'})

@login_required
@user_passes_test(is_organizador)
def evento_edit(request, pk):
    evento = get_object_or_404(Evento, pk=pk, organizador=request.user)
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('meus-eventos')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = EventoForm(instance=evento)
    return render(request, 'core/evento_form.html', {'form': form, 'action': 'Editar'})

@login_required
@user_passes_test(is_organizador)
def evento_delete(request, pk):
    evento = get_object_or_404(Evento, pk=pk, organizador=request.user)
    if request.method == 'POST':
        # Verifica se há inscrições
        if evento.inscricoes.exists():
            messages.error(request, 'Não é possível excluir um evento que possui inscrições.')
            return redirect('meus-eventos')
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('meus-eventos')
    return render(request, 'core/evento_confirm_delete.html', {'evento': evento})

@login_required
def inscrever_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if not evento.tem_vagas_disponiveis():
        messages.error(request, 'Desculpe, não há mais vagas disponíveis para este evento.')
        return redirect('evento_detail', pk=pk)
    
    if evento.esta_inscrito(request.user):
        messages.warning(request, 'Você já está inscrito neste evento.')
        return redirect('evento_detail', pk=pk)
    
    Inscricao.objects.create(evento=evento, usuario=request.user)
    messages.success(request, 'Inscrição realizada com sucesso!')
    return redirect('evento_detail', pk=pk)

@login_required
def cancelar_inscricao(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    inscricao = get_object_or_404(Inscricao, evento=evento, usuario=request.user)
    inscricao.delete()
    messages.success(request, 'Inscrição cancelada com sucesso!')
    return redirect('evento_detail', pk=pk)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'core/profile_edit.html', {'form': form})

@login_required
def profile_view_other(request, username):
    user = get_object_or_404(User, username=username)
    user_profile = user.profile
    eventos_participados = user_profile.get_eventos_participados()
    eventos_organizados = user_profile.get_eventos_organizados()
    
    context = {
        'user_profile': user_profile,
        'eventos_participados': eventos_participados,
        'eventos_organizados': eventos_organizados,
        'total_participados': user_profile.get_total_eventos_participados(),
        'total_organizados': user_profile.get_total_eventos_organizados(),
    }
    return render(request, 'core/profile_other.html', context)

@login_required
def meus_eventos_view(request):
    return render(request, 'meus-eventos.html')

@login_required
def meus_eventos(request):
    if request.user.tipo_usuario != 'organizador':
        return redirect('index')
    
    eventos = Evento.objects.filter(organizador=request.user).order_by('-data_hora')
    return render(request, 'core/meus_eventos.html', {
        'eventos': eventos
    })

@login_required
def criar_evento(request):
    if request.user.tipo_usuario != 'organizador':
        return redirect('index')
    
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user
            evento.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('meus_eventos')
    else:
        form = EventoForm()
    
    return render(request, 'core/evento_form.html', {
        'form': form,
        'action': 'Criar'
    })

@login_required
def editar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk, organizador=request.user)
    
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('meus_eventos')
    else:
        form = EventoForm(instance=evento)
    
    return render(request, 'core/evento_form.html', {
        'form': form,
        'evento': evento,
        'action': 'Editar'
    })

@login_required
def excluir_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk, organizador=request.user)
    
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('meus_eventos')
    
    return render(request, 'core/evento_confirm_delete.html', {
        'evento': evento
    })

@login_required
def preferencias(request):
    user = request.user
    email_form = EmailChangeForm(user, request.POST or None, prefix='email') if request.method == 'POST' and 'update_email' in request.POST else EmailChangeForm(user, prefix='email')
    password_form = PasswordChangeForm(user, request.POST or None, prefix='password') if request.method == 'POST' and 'update_password' in request.POST else PasswordChangeForm(user, prefix='password')

    # Uniformizar os campos do PasswordChangeForm
    for field in password_form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    password_form.fields['old_password'].label = 'Senha atual'
    password_form.fields['new_password1'].label = 'Senha nova'
    password_form.fields['new_password2'].label = 'Confirme a senha nova'

    email_success = None
    password_success = None

    if request.method == 'POST':
        if 'update_email' in request.POST:
            if email_form.is_valid():
                email_form.save()
                email_success = 'E-mail atualizado com sucesso.'
        elif 'update_password' in request.POST:
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                password_success = 'Senha alterada com sucesso.'

    return render(request, 'core/preferencias.html', {
        'user': user,
        'email_form': email_form,
        'password_form': password_form,
        'email_success': email_success,
        'password_success': password_success,
    })
 