// auth.js - Funções para autenticação e modais

// Funções de modal
function openModal(id) {
  console.log('Tentando abrir modal:', id);
  const modal = document.getElementById(id);
  const backdrop = document.querySelector('.modal-backdrop');
  
  if (modal) {
    modal.style.display = 'block';
    if (backdrop) {
      backdrop.style.display = 'block';
    }
    console.log('Modal aberto:', id);
  } else {
    console.error('Modal não encontrado:', id);
  }
}

function closeModal(id) {
  console.log('Tentando fechar modal:', id);
  const modal = document.getElementById(id);
  const backdrop = document.querySelector('.modal-backdrop');
  
  if (modal) {
    modal.style.display = 'none';
    if (backdrop) {
      backdrop.style.display = 'none';
    }
    console.log('Modal fechado:', id);
  } else {
    console.error('Modal não encontrado:', id);
  }
}

function gotoModal(from, to) {
  console.log('Tentando ir do modal', from, 'para', to);
  const fromModal = document.getElementById(from);
  const toModal = document.getElementById(to);
  const backdrop = document.querySelector('.modal-backdrop');
  
  if (fromModal && toModal) {
    fromModal.style.display = 'none';
    toModal.style.display = 'block';
    if (backdrop) {
      backdrop.style.display = 'block';
    }
    console.log('Navegação entre modais realizada');
  } else {
    console.error('Modal não encontrado:', fromModal ? to : from);
  }
}

// Função para toggle do dropdown do usuário
function toggleDropdown(event) {
  event.preventDefault();
  event.stopPropagation();
  var dropdown = document.getElementById('userDropdown');
  var isVisible = dropdown.style.display === 'block';
  
  // Close all dropdowns first
  dropdown.style.display = 'none';
  
  // If it was hidden, show it
  if (!isVisible) {
    dropdown.style.display = 'block';
    
    // Add click listener to close dropdown when clicking outside
    setTimeout(function() {
      document.addEventListener('click', function closeDropdown(e) {
        if (!e.target.closest('.dropdown')) {
          dropdown.style.display = 'none';
          document.removeEventListener('click', closeDropdown);
        }
      });
    }, 0);
  }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
  console.log('Auth.js carregado');
  
  // Configurar backdrop para fechar modais
  var backdrop = document.querySelector('.modal-backdrop');
  if (backdrop) {
    backdrop.onclick = function() {
      document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
      this.style.display = 'none';
    };
  }
  
  // Configurar dropdown global
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.dropdown')) {
      var dropdown = document.getElementById('userDropdown');
      if (dropdown) {
        dropdown.style.display = 'none';
      }
    }
  });
});
