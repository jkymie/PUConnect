from django.shortcuts import render
from django.utils import timezone
from .models import Evento, Categoria, Inscricao
from django.contrib.auth.decorators import login_required, user_passes_test

def home(request):
    agora = timezone.now()
    eventos_destaque = Evento.objects.filter(destaque=True, data_hora__gte=agora).order_by('data_hora')[:3]
    if not eventos_destaque:
        eventos_destaque = Evento.objects.filter(data_hora__gte=agora).order_by('data_hora')[:3]
    eventos_mes = Evento.objects.filter(data_hora__year=agora.year, data_hora__month=agora.month, data_hora__gte=agora).order_by('data_hora')[:3]
    categorias = Categoria.objects.all()
    return render(request, 'core/home.html', {
        'eventos_destaque': eventos_destaque,
        'eventos_mes': eventos_mes,
        'categorias': categorias,
    })

def index(request):
    return render(request, 'core/index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('home')
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
                return redirect('home')
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
    return user.is_authenticated and getattr(user, 'tipo_usuario', None) == 'organizador'

@login_required
@user_passes_test(is_organizador)
def evento_create(request):
    if not is_organizador(request.user):
        messages.error(request, 'Apenas organizadores podem criar eventos.')
        return redirect('home')
    
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user
            
            # Processa a imagem se foi enviada
            if 'imagem' in request.FILES:
                imagem = request.FILES['imagem']
                # Gera um nome único para o arquivo
                ext = os.path.splitext(imagem.name)[1]
                filename = f'eventos/{evento.titulo}_{timezone.now().strftime("%Y%m%d_%H%M%S")}{ext}'
                # Salva a imagem
                path = default_storage.save(filename, ContentFile(imagem.read()))
                evento.imagem = path
            
            evento.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('evento_detail', pk=evento.pk)
    else:
        form = EventoForm()
    
    return render(request, 'core/evento_form.html', {
        'form': form,
        'action': 'Criar'
    })

@login_required
@user_passes_test(is_organizador)
def evento_edit(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    
    if not is_organizador(request.user) or evento.organizador != request.user:
        messages.error(request, 'Você não tem permissão para editar este evento.')
        return redirect('evento_detail', pk=pk)
    
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            # Processa a imagem se foi enviada
            if 'imagem' in request.FILES:
                # Remove a imagem antiga se existir
                if evento.imagem:
                    default_storage.delete(evento.imagem.path)
                
                imagem = request.FILES['imagem']
                # Gera um nome único para o arquivo
                ext = os.path.splitext(imagem.name)[1]
                filename = f'eventos/{evento.titulo}_{timezone.now().strftime("%Y%m%d_%H%M%S")}{ext}'
                # Salva a nova imagem
                path = default_storage.save(filename, ContentFile(imagem.read()))
                evento.imagem = path
            
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('evento_detail', pk=pk)
    else:
        form = EventoForm(instance=evento)
    
    return render(request, 'core/evento_form.html', {
        'form': form,
        'action': 'Editar'
    })

@login_required
@user_passes_test(is_organizador)
def evento_delete(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    
    if not is_organizador(request.user) or evento.organizador != request.user:
        messages.error(request, 'Você não tem permissão para excluir este evento.')
        return redirect('evento_detail', pk=pk)
    
    if request.method == 'POST':
        # Remove a imagem se existir
        if evento.imagem:
            default_storage.delete(evento.imagem.path)
        
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('eventos_list')
    
    return render(request, 'core/evento_confirm_delete.html', {'evento': evento})

@login_required
def evento_detail(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    inscrito = evento.verificar_inscricao(request.user)
    vagas_disponiveis = evento.vagas_disponiveis()
    
    context = {
        'evento': evento,
        'inscrito': inscrito,
        'vagas_disponiveis': vagas_disponiveis,
        'form': InscricaoForm() if not inscrito and vagas_disponiveis > 0 else None
    }
    
    return render(request, 'core/evento_detail.html', context)

@login_required
def eventos_list(request):
    eventos = Evento.objects.all().order_by('-data_hora')
    return render(request, 'core/eventos_list.html', {'eventos': eventos})

@login_required
def evento_inscrever(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    
    if evento.verificar_inscricao(request.user):
        messages.error(request, 'Você já está inscrito neste evento.')
        return redirect('evento_detail', pk=pk)
    
    if evento.vagas_disponiveis <= 0:
        messages.error(request, 'Não há mais vagas disponíveis para este evento.')
        return redirect('evento_detail', pk=pk)
    
    if request.method == 'POST':
        form = InscricaoForm(request.POST)
        if form.is_valid():
            inscricao = form.save(commit=False)
            inscricao.evento = evento
            inscricao.usuario = request.user
            inscricao.save()
            messages.success(request, 'Inscrição realizada com sucesso!')
            return redirect('evento_detail', pk=pk)
    else:
        form = InscricaoForm()
    
    return render(request, 'core/evento_inscrever.html', {
        'form': form,
        'evento': evento
    })

@login_required
def evento_cancelar_inscricao(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    inscricao = get_object_or_404(Inscricao, evento=evento, usuario=request.user)
    
    if request.method == 'POST':
        inscricao.delete()
        messages.success(request, 'Inscrição cancelada com sucesso!')
        return redirect('evento_detail', pk=pk)
    
    return render(request, 'core/evento_cancelar_inscricao.html', {
        'evento': evento
    })

@login_required
def inscricoes(request):
    inscricoes = Inscricao.objects.filter(usuario=request.user).select_related('evento')
    return render(request, 'core/inscricoes.html', {'inscricoes': inscricoes})

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

@login_required
def meus_eventos_view(request):
    return render(request, 'meus-eventos.html')

@login_required
@user_passes_test(is_organizador)
def meus_eventos(request):
    if not is_organizador(request.user):
        messages.error(request, 'Apenas organizadores podem acessar esta página.')
        return redirect('home')
    
    eventos = Evento.objects.filter(organizador=request.user).order_by('-data_hora')
    return render(request, 'core/meus_eventos.html', {'eventos': eventos})
 