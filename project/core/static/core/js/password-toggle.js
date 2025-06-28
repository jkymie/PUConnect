// Password Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Função para criar o botão de toggle de senha
    function createPasswordToggle(input) {
        // Verificar se já existe um botão de toggle
        if (input.parentElement.querySelector('.password-toggle-btn')) {
            return;
        }

        // Criar wrapper se não existir
        let wrapper = input.parentElement;
        if (!wrapper.classList.contains('password-field-wrapper')) {
            wrapper = document.createElement('div');
            wrapper.className = 'password-field-wrapper';
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);
        }

        // Criar botão de toggle
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle-btn';
        toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
        toggleBtn.setAttribute('aria-label', 'Mostrar senha');

        // Adicionar evento de clique
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            
            // Atualizar ícone e estado
            const icon = toggleBtn.querySelector('i');
            if (isPassword) {
                icon.className = 'fas fa-eye-slash';
                toggleBtn.setAttribute('aria-label', 'Ocultar senha');
                toggleBtn.classList.add('showing');
            } else {
                icon.className = 'fas fa-eye';
                toggleBtn.setAttribute('aria-label', 'Mostrar senha');
                toggleBtn.classList.remove('showing');
            }
        });

        // Adicionar botão ao wrapper
        wrapper.appendChild(toggleBtn);
    }

    // Função para aplicar toggle em todos os campos de senha
    function applyPasswordToggles() {
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(createPasswordToggle);
    }

    // Aplicar inicialmente
    applyPasswordToggles();

    // Observer para campos de senha adicionados dinamicamente
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    const passwordInputs = node.querySelectorAll ? 
                        node.querySelectorAll('input[type="password"]') : [];
                    
                    if (node.matches && node.matches('input[type="password"]')) {
                        passwordInputs.push(node);
                    }
                    
                    passwordInputs.forEach(createPasswordToggle);
                }
            });
        });
    });

    // Observar mudanças no DOM
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // Aplicar novamente após um pequeno delay para garantir que modais sejam processados
    setTimeout(applyPasswordToggles, 100);
    
    // Aplicar quando modais são abertos (para o sistema de modais existente)
    if (typeof openModal === 'function') {
        const originalOpenModal = openModal;
        window.openModal = function(modalId) {
            originalOpenModal(modalId);
            setTimeout(applyPasswordToggles, 50);
        };
    }
}); 