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
}

document.addEventListener('DOMContentLoaded', function() {
  renderEventos();
  renderCentros();
});
