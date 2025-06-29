async function buscarEventos() {
  const resp = await fetch('/api/eventos/');
  if (!resp.ok) throw new Error('Erro ao buscar eventos');
  return await resp.json();
}

async function buscarCentros() {
  const resp = await fetch('/api/centros/');
  if (!resp.ok) throw new Error('Erro ao buscar centros');
  return await resp.json();
}

function formatarDataHora(dataStr) {
  const data = new Date(dataStr);
  const dia = String(data.getDate()).padStart(2, '0');
  const mes = String(data.getMonth() + 1).padStart(2, '0');
  const ano = data.getFullYear();
  const hora = String(data.getHours()).padStart(2, '0');
  const min = String(data.getMinutes()).padStart(2, '0');
  return `${dia}/${mes} | ${hora}:${min}`;
}

function getProximidadeTemporal(dataEvento) {
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  
  const dataEventoDate = new Date(dataEvento);
  dataEventoDate.setHours(0, 0, 0, 0);
  
  const amanha = new Date(hoje);
  amanha.setDate(amanha.getDate() + 1);
  
  const fimSemana = new Date(hoje);
  fimSemana.setDate(fimSemana.getDate() + 7);
  
  if (dataEventoDate.getTime() === hoje.getTime()) {
    return { tipo: 'hoje', texto: 'Hoje' };
  } else if (dataEventoDate.getTime() === amanha.getTime()) {
    return { tipo: 'amanha', texto: 'Amanhã' };
  } else if (dataEventoDate <= fimSemana) {
    return { tipo: 'semana', texto: 'Essa semana' };
  } else if (dataEventoDate.getMonth() === hoje.getMonth() && dataEventoDate.getFullYear() === hoje.getFullYear()) {
    return { tipo: 'mes', texto: 'Esse mês' };
  }
  return null;
}

function criarCard(evento) {
  // Se imagem for null, usar um placeholder
  const imgUrl = evento.imagem ? evento.imagem : '/static/core/assets/img/placeholder.jpg';
  
  // Calcular proximidade temporal
  const proximidade = getProximidadeTemporal(evento.data_hora);
  const tagProximidade = proximidade ? 
    `<span class="evento-tag evento-tag-proximidade ${proximidade.tipo}">${proximidade.texto}</span>` : '';
  
  return `
    <a href="/evento/${evento.id}/" class="card-evento-link">
      <div class="card-evento">
        <img src="${imgUrl}" alt="${evento.titulo}" class="card-evento-img">
        <div class="card-evento-body">
          <div class="card-evento-titulo">${evento.titulo}</div>
          <div class="card-evento-info">
            <span class="icon"><img src="/static/core/assets/img/clock.svg" alt="Horário" class="icon-img"></span>
            <span>${formatarDataHora(evento.data_hora)}</span>
          </div>
          <div class="card-evento-info">
            <span class="icon"><img src="/static/core/assets/img/local.png" alt="Local" class="icon-img"></span>
            <span>${evento.local}</span>
          </div>
          ${tagProximidade ? `<div style="margin-top: 8px;">${tagProximidade}</div>` : ''}
        </div>
      </div>
    </a>
  `;
}

function getCentroIcon(codigo) {
  const icons = {
    'ctch': 'fas fa-church',
    'ccs': 'fas fa-users',
    'ctc': 'fas fa-microchip',
    'ccbs': 'fas fa-heartbeat'
  };
  return icons[codigo] || 'fas fa-building';
}

function criarCentroCard(centro) {
  return `
    <a href="/eventos/?centro=${centro.codigo}" class="centro-card">
      <div class="centro-icon">
        <i class="${getCentroIcon(centro.codigo)}"></i>
      </div>
      <div class="centro-sigla">${centro.codigo.toUpperCase()}</div>
      <div class="centro-nome">${centro.nome}</div>
    </a>
  `;
}

async function renderCentros() {
  let centros = [];
  try {
    centros = await buscarCentros();
  } catch (e) {
    const centrosGrid = document.getElementById('centrosGrid');
    centrosGrid.innerHTML = '<p style="color:#155de2; text-align: center;">Erro ao carregar centros.</p>';
    return;
  }

  const centrosGrid = document.getElementById('centrosGrid');
  centrosGrid.innerHTML = centros.length
    ? centros.map(criarCentroCard).join('')
    : '<p style="color:#155de2; text-align: center;">Nenhum centro encontrado.</p>';
}

// Variáveis globais para o carrossel
let currentSlide = 0;
let totalSlides = 0;
let slidesPerView = 3; // Número de slides visíveis por vez

// Função para calcular quantos slides cabem na tela
function calculateSlidesPerView() {
  const container = document.querySelector('.carousel-wrapper');
  if (!container) return 3;
  
  const containerWidth = container.offsetWidth;
  const cardWidth = 300; // Largura do card
  const gap = 16; // Gap entre cards
  const padding = 40; // Padding total (20px de cada lado)
  
  // Calcula quantos cards cabem na tela
  const availableWidth = containerWidth - padding;
  const cardsPerView = Math.floor(availableWidth / (cardWidth + gap));
  return Math.max(1, cardsPerView); // Mínimo de 1 card
}

// Função para criar indicadores do carrossel
function createIndicators() {
  const indicatorsContainer = document.getElementById('carouselIndicators');
  const track = document.getElementById('listaEventosDestaque');
  
  if (!indicatorsContainer || !track) return;
  
  const cards = track.querySelectorAll('.card-evento');
  const currentSlidesPerView = calculateSlidesPerView();
  const totalPages = Math.ceil(cards.length / currentSlidesPerView);
  
  // Limpa indicadores existentes
  indicatorsContainer.innerHTML = '';
  
  // Cria indicadores apenas se há mais de uma página
  if (totalPages > 1) {
    for (let i = 0; i < totalPages; i++) {
      const indicator = document.createElement('button');
      indicator.className = 'carousel-indicator';
      indicator.setAttribute('aria-label', `Ir para página ${i + 1} dos eventos`);
      indicator.setAttribute('data-slide', i);
      
      indicator.addEventListener('click', () => {
        currentSlide = i * currentSlidesPerView;
        updateCarousel();
      });
      
      indicator.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          currentSlide = i * currentSlidesPerView;
          updateCarousel();
        }
      });
      
      indicatorsContainer.appendChild(indicator);
    }
  }
}

// Função para atualizar indicadores
function updateIndicators() {
  const indicators = document.querySelectorAll('.carousel-indicator');
  const currentSlidesPerView = calculateSlidesPerView();
  const currentPage = Math.floor(currentSlide / currentSlidesPerView);
  
  indicators.forEach((indicator, index) => {
    if (index === currentPage) {
      indicator.classList.add('active');
      indicator.setAttribute('aria-current', 'true');
    } else {
      indicator.classList.remove('active');
      indicator.removeAttribute('aria-current');
    }
  });
}

// Função para atualizar o carrossel
function updateCarousel() {
  const track = document.getElementById('listaEventosDestaque');
  const prevBtn = document.getElementById('carouselPrev');
  const nextBtn = document.getElementById('carouselNext');
  
  if (!track || !prevBtn || !nextBtn) return;
  
  // Recalcula slides por view baseado no tamanho da tela
  slidesPerView = calculateSlidesPerView();
  
  // Calcula o total de slides
  const cards = track.querySelectorAll('.card-evento');
  totalSlides = Math.max(0, cards.length - slidesPerView);
  
  // Atualiza a posição do carrossel
  const cardWidth = 300; // Largura do card
  const gap = 16; // Gap entre cards
  const translateX = -currentSlide * (cardWidth + gap);
  track.style.transform = `translateX(${translateX}px)`;
  
  // Atualiza estado dos botões
  prevBtn.disabled = currentSlide === 0;
  nextBtn.disabled = currentSlide >= totalSlides;
  
  // Esconde os botões se não há necessidade de navegação
  if (cards.length <= slidesPerView) {
    prevBtn.style.display = 'none';
    nextBtn.style.display = 'none';
  } else {
    prevBtn.style.display = 'flex';
    nextBtn.style.display = 'flex';
  }
  
  // Atualiza indicadores
  updateIndicators();
}

// Função para ir para o próximo slide
function nextSlide() {
  if (currentSlide < totalSlides) {
    currentSlide++;
    updateCarousel();
  }
}

// Função para ir para o slide anterior
function prevSlide() {
  if (currentSlide > 0) {
    currentSlide--;
    updateCarousel();
  }
}

// Função para inicializar o carrossel
function initCarousel() {
  const prevBtn = document.getElementById('carouselPrev');
  const nextBtn = document.getElementById('carouselNext');
  
  if (prevBtn && nextBtn) {
    // Adiciona listeners para os botões
    prevBtn.addEventListener('click', prevSlide);
    nextBtn.addEventListener('click', nextSlide);
    
    // Adiciona suporte para navegação por teclado
    prevBtn.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        prevSlide();
      }
    });
    
    nextBtn.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        nextSlide();
      }
    });
    
    // Adiciona suporte para setas do teclado quando o carrossel está em foco
    const carouselContainer = document.querySelector('.carousel-container');
    if (carouselContainer) {
      carouselContainer.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
          e.preventDefault();
          prevSlide();
        } else if (e.key === 'ArrowRight') {
          e.preventDefault();
          nextSlide();
        }
      });
      
      // Torna o container focável para navegação por teclado
      carouselContainer.setAttribute('tabindex', '0');
    }
    
    // Atualiza o carrossel quando a janela é redimensionada
    window.addEventListener('resize', () => {
      currentSlide = 0; // Volta para o início
      updateCarousel();
      createIndicators(); // Recria indicadores com novo tamanho
    });
    
    // Inicializa o carrossel
    updateCarousel();
    createIndicators();
  }
}

// --- Carrossel Eventos do Mês ---
let currentSlideMes = 0;
let totalSlidesMes = 0;
let slidesPerViewMes = 3;

function calculateSlidesPerViewMes() {
  const container = document.querySelector('.carousel-wrapper-mes');
  if (!container) return 3;
  const containerWidth = container.offsetWidth;
  const cardWidth = 300;
  const gap = 16;
  const padding = 40;
  const availableWidth = containerWidth - padding;
  const cardsPerView = Math.floor(availableWidth / (cardWidth + gap));
  return Math.max(1, cardsPerView);
}

function updateCarouselMes() {
  const track = document.getElementById('listaEventosMes');
  const prevBtn = document.getElementById('carouselPrevMes');
  const nextBtn = document.getElementById('carouselNextMes');
  if (!track || !prevBtn || !nextBtn) return;
  slidesPerViewMes = calculateSlidesPerViewMes();
  const cards = track.querySelectorAll('.card-evento');
  totalSlidesMes = Math.max(0, cards.length - slidesPerViewMes);
  const cardWidth = 300;
  const gap = 16;
  const translateX = -currentSlideMes * (cardWidth + gap);
  track.style.transform = `translateX(${translateX}px)`;
  prevBtn.disabled = currentSlideMes === 0;
  nextBtn.disabled = currentSlideMes >= totalSlidesMes;
  // Setas SEMPRE visíveis
  prevBtn.style.display = 'flex';
  nextBtn.style.display = 'flex';
}

function nextSlideMes() {
  if (currentSlideMes < totalSlidesMes) {
    currentSlideMes++;
    updateCarouselMes();
  }
}
function prevSlideMes() {
  if (currentSlideMes > 0) {
    currentSlideMes--;
    updateCarouselMes();
  }
}
function initCarouselMes() {
  const prevBtn = document.getElementById('carouselPrevMes');
  const nextBtn = document.getElementById('carouselNextMes');
  if (prevBtn && nextBtn) {
    prevBtn.addEventListener('click', prevSlideMes);
    nextBtn.addEventListener('click', nextSlideMes);
    window.addEventListener('resize', () => {
      currentSlideMes = 0;
      updateCarouselMes();
    });
    updateCarouselMes();
  }
}

// --- Fim Carrossel Eventos do Mês ---

async function renderEventos() {
  let eventos = [];
  try {
    eventos = await buscarEventos();
  } catch (e) {
    const listaDestaque = document.getElementById('listaEventosDestaque');
    const listaMes = document.getElementById('listaEventosMes');
    listaDestaque.innerHTML = '<p style="color:#155de2">Erro ao carregar eventos.</p>';
    listaMes.innerHTML = '<p style="color:#155de2">Erro ao carregar eventos.</p>';
    return;
  }
  const agora = new Date();
  const mesAtual = agora.getMonth();
  const anoAtual = agora.getFullYear();

  // Eventos em destaque: futuros, ordenados pelo mais próximo
  const eventosDestaque = eventos
    .filter(e => new Date(e.data_hora) > agora)
    .sort((a, b) => new Date(a.data_hora) - new Date(b.data_hora));

  // Eventos desse mês
  const eventosMes = eventos.filter(e => {
    const data = new Date(e.data_hora);
    return data.getMonth() === mesAtual && data.getFullYear() === anoAtual;
  });

  const listaDestaque = document.getElementById('listaEventosDestaque');
  const listaMes = document.getElementById('listaEventosMes');

  listaDestaque.innerHTML = eventosDestaque.length
    ? eventosDestaque.map(criarCard).join('')
    : '<p style="color:#155de2">Nenhum evento em destaque.</p>';

  listaMes.innerHTML = eventosMes.length
    ? eventosMes.map(criarCard).join('')
    : '<p style="color:#155de2">Nenhum evento neste mês.</p>';
    
  // Inicializa o carrossel após carregar os eventos
  setTimeout(() => {
    initCarousel();
    initCarouselMes();
  }, 100);
}

document.addEventListener('DOMContentLoaded', function() {
  renderEventos();
  renderCentros();
});
