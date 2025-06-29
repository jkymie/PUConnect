// main.js

function carregarComponente(id, arquivo) {
    fetch(arquivo)
      .then(res => res.text())
      .then(html => {
        document.getElementById(id).innerHTML = html;
      });
  }

// Função para gerenciar alertas
function initAlerts() {
  const alerts = document.querySelectorAll('.alert');
  
  alerts.forEach(alert => {
    // Auto-remove após 5 segundos
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
    
    // Melhorar o botão de fechar
    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function() {
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

// Função para verificar se há mensagens e garantir que sejam exibidas
function checkForMessages() {
  const alertsContainer = document.querySelector('.alerts-container');
  if (alertsContainer && alertsContainer.children.length > 0) {
    // Se há mensagens, garantir que elas sejam visíveis
    alertsContainer.style.display = 'block';
    initAlerts();
  }
}

// Função para forçar recarregamento sem cache
function forceReload() {
  window.location.reload(true);
}

// Função para criar alertas dinamicamente
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
  
  // Inicializar o alerta
  setTimeout(() => {
    initAlerts();
  }, 100);
}

// Função para verificar se há mensagens na URL (para casos de redirect)
function checkUrlMessages() {
  const urlParams = new URLSearchParams(window.location.search);
  const message = urlParams.get('message');
  const messageType = urlParams.get('type') || 'success';
  
  if (message) {
    createAlert(decodeURIComponent(message), messageType);
    // Limpar a URL
    const newUrl = window.location.pathname;
    window.history.replaceState({}, document.title, newUrl);
  }
}

document.addEventListener('DOMContentLoaded', function () {
  // Inicializar alertas
  initAlerts();
  
  // Verificar se há mensagens e garantir que sejam exibidas
  checkForMessages();
  
  // Verificar se há mensagens na URL
  checkUrlMessages();
  
  // Verificar se a página foi carregada após um logout (URL pode conter parâmetros)
  if (window.location.search.includes('logout') || document.referrer.includes('logout')) {
    // Forçar recarregamento para garantir que as mensagens sejam exibidas
    setTimeout(() => {
      if (document.querySelector('.alerts-container .alert')) {
        // Se há alertas, garantir que sejam visíveis
        document.querySelector('.alerts-container').style.display = 'block';
      }
    }, 100);
  }
  
  const input = document.getElementById('searchInput');
  const button = document.getElementById('searchButton');

  input.addEventListener('input', () => {
    if (input.value.trim() !== '') {
      button.style.display = 'inline-block'; // more consistent
    } else {
      button.style.display = 'none';
    }
  });

  // Funções de modal - Movidas para auth.js para evitar conflitos
  /*
  window.openModal = function(id) {
    document.getElementById(id).style.display = 'block';
    document.querySelector('.modal-backdrop').style.display = 'block';
  }
  window.closeModal = function(id) {
    document.getElementById(id).style.display = 'none';
    document.querySelector('.modal-backdrop').style.display = 'none';
  }
  window.gotoModal = function(from, to) {
    document.getElementById(from).style.display = 'none';
    document.getElementById(to).style.display = 'block';
    document.querySelector('.modal-backdrop').style.display = 'block';
  }
  var backdrop = document.querySelector('.modal-backdrop');
  if (backdrop) {
    backdrop.onclick = function() {
      document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
      this.style.display = 'none';
    };
  }
  */

  // --- Recuperação de senha via AJAX ---
  var forgotForm = document.querySelector('#modal-forgot form');
  if (forgotForm) {
    forgotForm.onsubmit = async function(e) {
      e.preventDefault();
      const email = this.email.value;
      const resp = await fetch('/password-reset/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `email=${encodeURIComponent(email)}`
      });
      const data = await resp.json();
      if (data.success) {
        gotoModal('modal-forgot', 'modal-verify');
      } else {
        alert(data.error || 'Erro ao enviar e-mail.');
      }
    }
  }
  var verifyForm = document.querySelector('#modal-verify form');
  if (verifyForm) {
    verifyForm.onsubmit = async function(e) {
      e.preventDefault();
      const code = this.code.value;
      const resp = await fetch('/password-reset/verify/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `code=${encodeURIComponent(code)}`
      });
      const data = await resp.json();
      if (data.success) {
        gotoModal('modal-verify', 'modal-newpass');
      } else {
        alert(data.error || 'Código inválido.');
      }
    }
  }
  var newpassForm = document.querySelector('#modal-newpass form');
  if (newpassForm) {
    newpassForm.onsubmit = async function(e) {
      e.preventDefault();
      const senha1 = this.new_password1.value;
      const senha2 = this.new_password2.value;
      const resp = await fetch('/password-reset/new/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `new_password1=${encodeURIComponent(senha1)}&new_password2=${encodeURIComponent(senha2)}`
      });
      const data = await resp.json();
      if (data.success) {
        alert('Senha alterada com sucesso! Faça login com a nova senha.');
        closeModal('modal-newpass');
        openModal('modal-login');
      } else {
        alert(data.error || 'Erro ao atualizar senha.');
      }
    }
  }

  // --- Cadastro via AJAX ---
  var registerForm = document.querySelector('#modal-register form');
  if (registerForm) {
    registerForm.onsubmit = async function(e) {
      e.preventDefault();
      // Limpa erros antigos
      var oldErrors = registerForm.querySelectorAll('.form-error');
      oldErrors.forEach(e => e.remove());
      var btn = this.querySelector('button[type=submit]');
      btn.disabled = true;
      const formData = new FormData(this);
      const resp = await fetch('/register-modal/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: formData
      });
      const data = await resp.json();
      btn.disabled = false;
      if (data.success) {
        alert('Conta criada com sucesso! Você já está logado.');
        closeModal('modal-register');
        window.location.reload();
      } else {
        // Exibe erros no modal
        for (const [field, msgs] of Object.entries(data.errors)) {
          let el;
          if (field === '__all__') {
            el = registerForm;
          } else {
            el = registerForm.querySelector(`[name="${field}"]`);
          }
          if (el) {
            const div = document.createElement('div');
            div.className = 'form-error';
            div.style.color = '#c62828';
            div.style.margin = '6px 0 0 0';
            div.style.fontSize = '15px';
            div.innerHTML = msgs.map(m => `<span>• ${m}</span>`).join('<br>');
            if (el.parentNode) {
              if (field === '__all__') {
                el.insertBefore(div, el.firstChild);
              } else {
                el.parentNode.appendChild(div);
              }
            }
          }
        }
      }
    }
  }

  // --- Login via AJAX ---
  var loginForm = document.querySelector('#modal-login form');
  if (loginForm) {
    loginForm.onsubmit = async function(e) {
      e.preventDefault();
      // Limpa erros antigos
      var oldErrors = loginForm.querySelectorAll('.form-error');
      oldErrors.forEach(e => e.remove());
      var btn = this.querySelector('button[type=submit]');
      btn.disabled = true;
      const formData = new FormData(this);
      const resp = await fetch('/login-modal/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: formData
      });
      const data = await resp.json();
      btn.disabled = false;
      if (data.success) {
        closeModal('modal-login');
        window.location.reload();
      } else {
        // Exibe erros no modal
        for (const [field, msgs] of Object.entries(data.errors)) {
          let el;
          if (field === '__all__') {
            el = loginForm;
          } else {
            el = loginForm.querySelector(`[name="${field}"]`);
          }
          if (el) {
            const div = document.createElement('div');
            div.className = 'form-error';
            div.style.color = '#c62828';
            div.style.margin = '6px 0 0 0';
            div.style.fontSize = '15px';
            div.innerHTML = msgs.map(m => `<span>• ${m}</span>`).join('<br>');
            if (el.parentNode) {
              if (field === '__all__') {
                el.insertBefore(div, el.firstChild);
              } else {
                el.parentNode.appendChild(div);
              }
            }
          }
        }
      }
    }
  }
});