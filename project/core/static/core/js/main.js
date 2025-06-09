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

  input.addEventListener('input', () => {
    if (input.value.trim() !== '') {
      button.style.display = 'inline-block'; // more consistent
    } else {
      button.style.display = 'none';
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
});