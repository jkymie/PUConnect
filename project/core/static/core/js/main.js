
// Função para carregar componente por ID e URL
function carregarComponente(id, arquivo) {
  fetch(arquivo)
    .then(res => res.text())
    .then(html => {
      document.getElementById(id).innerHTML = html;
    });
}

// Funções de alerta
function initAlerts() {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      if (alert && alert.parentElement) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-20px)';
        setTimeout(() => {
          if (alert.parentElement) {
            alert.parentElement.removeChild(alert);
          }
        }, 300);
      }
    }, 5000);

    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-20px)';
        setTimeout(() => {
          if (alert.parentElement) {
            alert.parentElement.removeChild(alert);
          }
        }, 300);
      });
    }
  });
}

function checkForMessages() {
  const alertsContainer = document.querySelector('.alerts-container');
  if (alertsContainer && alertsContainer.children.length > 0) {
    alertsContainer.style.display = 'block';
    initAlerts();
  }
}

function createAlert(message, type = 'success') {
  const alertsContainer = document.querySelector('.alerts-container');
  if (!alertsContainer) return;

  const alert = document.createElement('div');
  alert.className = `alert alert-${type}`;
  alert.innerHTML = `
    ${message}
    <button type="button" class="alert-close" onclick="this.parentElement.style.display='none'">&times;</button>
  `;
  alertsContainer.appendChild(alert);

  setTimeout(() => {
    initAlerts();
  }, 100);
}

function checkUrlMessages() {
  const urlParams = new URLSearchParams(window.location.search);
  const message = urlParams.get('message');
  const messageType = urlParams.get('type') || 'success';

  if (message) {
    createAlert(decodeURIComponent(message), messageType);
    const newUrl = window.location.pathname;
    window.history.replaceState({}, document.title, newUrl);
  }
}

// Carrossel: Opacidade dinâmica
function atualizarOpacidadeCarrossel(id) {
  const container = document.getElementById(id);
  if (!container) return;

  const cards = container.querySelectorAll('.card-evento');
  const containerRect = container.getBoundingClientRect();
  const center = containerRect.left + containerRect.width / 2;

  const fadeStartZone = containerRect.width * 0.30;

  cards.forEach(card => {
    const cardRect = card.getBoundingClientRect();
    const cardCenter = cardRect.left + cardRect.width / 2;
    const distance = Math.abs(center - cardCenter);

    let opacity = 1;
    if (distance > fadeStartZone) {
      const maxDistance = containerRect.width / 2;
      const fadeDistance = maxDistance - fadeStartZone;
      opacity = Math.max(0.1, 1 - ((distance - fadeStartZone) / fadeDistance));
    }

    card.style.opacity = opacity.toFixed(2);
  });
}

// Carrossel: scroll com botão
function scrollCarrossel(id, direction) {
  const el = document.getElementById(id);
  const amount = el.offsetWidth * 0.85 * direction;
  el.scrollBy({ left: amount, behavior: 'smooth' });
  setTimeout(() => atualizarOpacidadeCarrossel(id), 250);
}
window.scrollCarrossel = scrollCarrossel;

// Carrossel: drag/touch
function enableCarrosselDrag(id) {
  const container = document.getElementById(id);
  if (!container) return;

  let isDown = false;
  let startX, scrollLeft;

  container.addEventListener('mousedown', (e) => {
    isDown = true;
    container.classList.add('dragging');
    startX = e.pageX - container.offsetLeft;
    scrollLeft = container.scrollLeft;
  });

  container.addEventListener('mouseleave', () => {
    isDown = false;
    container.classList.remove('dragging');
  });

  container.addEventListener('mouseup', () => {
    isDown = false;
    container.classList.remove('dragging');
  });

  container.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - container.offsetLeft;
    const walk = (x - startX) * 1.5;
    container.scrollLeft = scrollLeft - walk;
    atualizarOpacidadeCarrossel(id);
  });

  container.addEventListener('touchstart', (e) => {
    isDown = true;
    startX = e.touches[0].pageX - container.offsetLeft;
    scrollLeft = container.scrollLeft;
  });

  container.addEventListener('touchend', () => {
    isDown = false;
  });

  let wasDragging = false;
  container.addEventListener('mousedown', () => { wasDragging = false; });
  container.addEventListener('mousemove', () => { wasDragging = true; });
  container.addEventListener('click', (e) => {
    if (wasDragging) {
      e.preventDefault();
      e.stopPropagation();
    }
  });

  container.addEventListener('touchmove', (e) => {
    if (!isDown) return;
    const x = e.touches[0].pageX - container.offsetLeft;
    const walk = (x - startX) * 1.5;
    container.scrollLeft = scrollLeft - walk;
    atualizarOpacidadeCarrossel(id);
  });

  container.addEventListener('scroll', () => {
    requestAnimationFrame(() => atualizarOpacidadeCarrossel(id));
  });

  atualizarOpacidadeCarrossel(id);
}

// DOM ready
document.addEventListener('DOMContentLoaded', () => {
  initAlerts();
  checkForMessages();
  checkUrlMessages();

  const ids = ["listaEventosDestaque", "listaEventosMes"];
  ids.forEach(id => {
    enableCarrosselDrag(id);
    setTimeout(() => atualizarOpacidadeCarrossel(id), 50);
  });

  window.addEventListener('resize', () => {
    ids.forEach(id => atualizarOpacidadeCarrossel(id));
  });

  const input = document.getElementById('searchInput');
  const button = document.getElementById('searchButton');
  if (input && button) {
    input.addEventListener('input', () => {
      button.style.display = input.value.trim() !== '' ? 'inline-block' : 'none';
    });
  }

  function togglePassword(inputId, toggleId) {
    const input = document.getElementById(inputId);
    const toggle = document.getElementById(toggleId);
    if (input && toggle) {
      toggle.addEventListener('click', () => {
        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';
        toggle.innerHTML = isPassword
          ? '<i class="bi bi-eye-slash"></i>'
          : '<i class="bi bi-eye"></i>';
      });
    }
  }

  togglePassword('login-password', 'toggleLoginPassword');  
  togglePassword('register-password1', 'toggleRegisterPassword');
  togglePassword('register-password2', 'toggleRegisterPassword2');
  togglePassword('old_password', 'toggleOldPassword');
  togglePassword('new_password1', 'toggleNewPassword1');
  togglePassword('new_password2', 'toggleNewPassword2');

  window.openModal = function (id) {
    document.getElementById(id).style.display = 'block';
    document.querySelector('.modal-backdrop').style.display = 'block';
  };
  window.closeModal = function (id) {
    document.getElementById(id).style.display = 'none';
    document.querySelector('.modal-backdrop').style.display = 'none';
  };
  window.gotoModal = function (from, to) {
    document.getElementById(from).style.display = 'none';
    document.getElementById(to).style.display = 'block';
    document.querySelector('.modal-backdrop').style.display = 'block';
  };

  const backdrop = document.querySelector('.modal-backdrop');
  if (backdrop) {
    backdrop.onclick = function () {
      document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
      this.style.display = 'none';
    };
  }
});

