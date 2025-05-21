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
});