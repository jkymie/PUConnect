from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .forms import UserRegistrationForm, UserLoginForm, EventoForm, SolicitarOrganizadorForm, UserProfileForm
from .models import Evento, Inscricao, SolicitarOrganizador, UserProfile

def index(request):
    return render(request, 'core/index.html')

@login_required
def inscricoes(request):
    inscricoes = Inscricao.objects.filter(usuario=request.user).select_related('evento').order_by('-data_inscricao')
    return render(request, 'core/inscricoes.html', {'inscricoes': inscricoes})

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
    # Se o usuário já estiver logado, redireciona para home
    if request.user.is_authenticated:
        return redirect('home')
        
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

def logout_view(request):
    if request.user.is_authenticated:
        auth_logout(request)
        messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('index')

@login_required
def home(request):
    return render(request, 'core/home.html')

def eventos_list(request):
    eventos = Evento.objects.all().order_by('-data_hora')
    for evento in eventos:
        evento._current_user = request.user
    return render(request, 'core/eventos_list.html', {
        'eventos': eventos
    })

def is_organizador(user):
    return user.is_authenticated and user.tipo_usuario == 'organizador'

@user_passes_test(is_organizador)
def evento_create(request):
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user
            evento.save()
            messages.success(request, 'Evento cadastrado com sucesso!')
            return redirect('eventos_list')
    else:
        form = EventoForm()
    return render(request, 'core/evento_create.html', {'form': form})

@login_required
def inscrever_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    
    # Verifica se o usuário já está inscrito
    if evento.esta_inscrito(request.user):
        messages.info(request, f'Você já está inscrito neste evento.')
        return redirect('eventos_list')
    
    # Verifica se há vagas disponíveis
    if not evento.tem_vagas_disponiveis():
        messages.error(request, f'Desculpe, não há mais vagas disponíveis para este evento.')
        return redirect('eventos_list')
    
    # Cria a inscrição
    inscricao = Inscricao.objects.create(
        evento=evento,
        usuario=request.user
    )
    
    messages.success(request, f'Inscrição realizada com sucesso para o evento {evento.titulo}!')
    return redirect('eventos_list')

@login_required
def marcar_presenca(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    inscricao = get_object_or_404(Inscricao, evento=evento, usuario=request.user)
    inscricao.presente = not inscricao.presente
    inscricao.save()
    status = "presente" if inscricao.presente else "ausente"
    messages.success(request, f'Presença marcada como {status} no evento {evento.titulo}.')
    return redirect('eventos_list')

@login_required
def solicitar_organizador(request):
    # Verifica se já existe uma solicitação pendente
    if SolicitarOrganizador.objects.filter(usuario=request.user, status='pendente').exists():
        messages.warning(request, 'Você já possui uma solicitação pendente.')
        return redirect('home')
    
    # Verifica se já é organizador
    if request.user.tipo_usuario == 'organizador':
        messages.info(request, 'Você já é um organizador.')
        return redirect('home')
    
    if request.method == 'POST':
        form = SolicitarOrganizadorForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.usuario = request.user
            solicitacao.save()
            messages.success(request, 'Sua solicitação foi enviada com sucesso!')
            return redirect('home')
    else:
        form = SolicitarOrganizadorForm()
    
    return render(request, 'core/solicitar_organizador.html', {'form': form})

@login_required
def minhas_solicitacoes(request):
    if request.user.tipo_usuario != 'admin':
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    solicitacoes = SolicitarOrganizador.objects.all().select_related('usuario')
    return render(request, 'core/minhas_solicitacoes.html', {'solicitacoes': solicitacoes})

@login_required
def responder_solicitacao(request, solicitacao_id):
    if request.user.tipo_usuario != 'admin':
        messages.error(request, 'Acesso não autorizado.')
        return redirect('home')
    
    solicitacao = get_object_or_404(SolicitarOrganizador, id=solicitacao_id)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        resposta = request.POST.get('resposta', '')
        
        if acao in ['aprovar', 'rejeitar']:
            solicitacao.status = 'aprovado' if acao == 'aprovar' else 'rejeitado'
            solicitacao.resposta = resposta
            solicitacao.data_resposta = timezone.now()
            solicitacao.save()
            
            if acao == 'aprovar':
                solicitacao.usuario.tipo_usuario = 'organizador'
                solicitacao.usuario.save()
                messages.success(request, f'Solicitação aprovada. {solicitacao.usuario.username} agora é um organizador.')
            else:
                messages.success(request, 'Solicitação rejeitada.')
            
            return redirect('minhas_solicitacoes')
    
    return render(request, 'core/responder_solicitacao.html', {'solicitacao': solicitacao})

@login_required
def profile_view(request):
    user_profile = request.user.profile
    eventos_participados = user_profile.get_eventos_participados()
    eventos_organizados = user_profile.get_eventos_organizados()
    
    context = {
        'user_profile': user_profile,
        'eventos_participados': eventos_participados,
        'eventos_organizados': eventos_organizados,
        'total_participados': user_profile.get_total_eventos_participados(),
        'total_organizados': user_profile.get_total_eventos_organizados(),
    }
    return render(request, 'core/profile.html', context)

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

 