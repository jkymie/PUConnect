// main.js

function carregarComponente(id, arquivo) {
    fetch(arquivo)
      .then(res => res.text())
      .then(html => {
        document.getElementById(id).innerHTML = html;
      });
  }
