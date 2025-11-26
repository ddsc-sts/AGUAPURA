// Seleciona todos os botões de aba
const tabs = document.querySelectorAll(".perfil-tab");

// Seleciona todo o conteúdo das abas
const conteudos = document.querySelectorAll(".tab-content");

// Para cada botão, adiciona o evento de clique
tabs.forEach(tab => {
    tab.addEventListener("click", () => {

        // Remove 'active' de todos os botões
        tabs.forEach(t => t.classList.remove("active"));

        // Adiciona 'active' ao botão clicado
        tab.classList.add("active");

        // Esconde todas as abas
        conteudos.forEach(c => c.classList.remove("active"));

        // Mostra só a aba clicada
        const alvo = document.getElementById(tab.dataset.tab);
        alvo.classList.add("active");
    });
});

