async function buscarEventos() {
  const resp = await fetch('/api/eventos/');
  if (!resp.ok) throw new Error('Erro ao buscar eventos');
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

function criarCard(evento) {
  // Se imagem for null, usar um placeholder
  const imgUrl = evento.imagem ? evento.imagem : '/static/core/assets/img/placeholder.jpg';
  return `
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
      </div>
    </div>
  `;
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

document.addEventListener('DOMContentLoaded', renderEventos);
