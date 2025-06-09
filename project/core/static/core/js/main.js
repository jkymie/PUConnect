// main.js

function carregarComponente(id, arquivo) {
    fetch(arquivo)
      .then(res => res.text())
      .then(html => {
        document.getElementById(id).innerHTML = html;
      });
  }

document.addEventListener('DOMContentLoaded', function () {
  const input = document.getElementById('searchInput');
  const button = document.getElementById('searchButton');

  if (input) {
    input.addEventListener('input', () => {
      if (input.value.trim() !== '') {
        button.style.display = 'inline-block';
      } else {
        button.style.display = 'none';
      }
    });
  }

  // Handle alert messages
  const alerts = document.querySelectorAll('.alert');
  const processedMessages = new Set();

  alerts.forEach(alert => {
    const messageContent = alert.textContent.trim();
    
    // If we've already processed this exact message, remove the duplicate
    if (processedMessages.has(messageContent)) {
      alert.remove();
    } else {
      processedMessages.add(messageContent);
      
      // Add auto-dismiss after 5 seconds
      setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
      }, 5000);

      // Handle manual close button
      const closeButton = alert.querySelector('.alert-close');
      if (closeButton) {
        closeButton.addEventListener('click', () => {
          alert.style.opacity = '0';
          setTimeout(() => alert.remove(), 300);
        });
      }
    }
  });

  // Funções de modal
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