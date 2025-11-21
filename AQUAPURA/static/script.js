document.addEventListener('DOMContentLoaded', () => {
  // ===== CARROSSEL =====
  const slidesContainer = document.querySelector('.slides');
  const slides = document.querySelectorAll('.slide');
  const prev = document.querySelector('.prev');
  const next = document.querySelector('.next');
  const dotsContainer = document.querySelector('.dots');

  let currentSlide = 0;

  if (slidesContainer && slides.length > 0) {
    slides.forEach((_, i) => {
      const dot = document.createElement('span');
      dot.classList.add('dot');
      if (i === 0) dot.classList.add('active');
      dot.addEventListener('click', () => goToSlide(i));
      dotsContainer.appendChild(dot);
    });

    const dots = document.querySelectorAll('.dot');

    function updateCarousel() {
      slidesContainer.style.transform = `translateX(-${currentSlide * 100}%)`;
      dots.forEach(dot => dot.classList.remove('active'));
      dots[currentSlide].classList.add('active');
    }

    function nextSlide() {
      currentSlide = (currentSlide + 1) % slides.length;
      updateCarousel();
    }

    function prevSlide() {
      currentSlide = (currentSlide - 1 + slides.length) % slides.length;
      updateCarousel();
    }

    function goToSlide(index) {
      currentSlide = index;
      updateCarousel();
    }

    if (next && prev) {
      next.addEventListener('click', nextSlide);
      prev.addEventListener('click', prevSlide);
    }

    setInterval(nextSlide, 5000);
  }

  // ===== MODO ESCURO / CLARO =====
  const toggle = document.querySelector('.theme-btn');
  const root = document.documentElement;
  const logo = document.getElementById('site-logo');

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);

    if (logo) {
      logo.style.transition = 'opacity 0.4s ease';
      logo.style.opacity = '0';
      setTimeout(() => {
        logo.src = theme === 'dark' ? logo.dataset.dark : logo.dataset.light;
        logo.style.opacity = '1';
      }, 200);
    }

    if (toggle) {
      toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
  }

  const savedTheme = localStorage.getItem('theme') || 'light';
  applyTheme(savedTheme);

  if (toggle) {
    toggle.addEventListener('click', () => {
      const current = root.getAttribute('data-theme');
      const newTheme = current === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);
    });
  }

  // ===== CHAT DE SUPORTE =====
  const chatContainer = document.getElementById("chat-container");
  const chatOpen = document.getElementById("chat-open");
  const chatClose = document.getElementById("chat-close");
  const chatBody = document.getElementById("chat-body");
  const chatInput = document.getElementById("chat-input");
  const chatSend = document.getElementById("chat-send");

  if (chatOpen && chatClose && chatContainer) {
    chatOpen.addEventListener("click", () => {
      chatContainer.classList.remove("hidden");
    });
    
    chatClose.addEventListener("click", () => {
      chatContainer.classList.add("hidden");
    });
  }

  const respostas = {
    "oi": "Olá! Como posso ajudar?",
    "ola": "Olá! Como posso ajudar?",
    "preço": "Todos os preços estão listados diretamente na página dos produtos.",
    "entrega": "Realizamos entregas em todo o Brasil. Qual sua cidade?",
    "frete": "O frete é grátis em compras acima de R$129,90 para Santa Catarina.",
    "troca": "Para trocas, consulte nossa Política de Troca no rodapé do site.",
    "horário": "Nosso suporte funciona 24h via site.",
    "pagamento": "Aceitamos Pix, cartão de crédito e boleto.",
    "default": "Desculpe, não entendi. Pode tentar reformular?"
  };

  function addMessage(text, type) {
    const div = document.createElement("div");
    div.classList.add(type === "user" ? "user-message" : "bot-message");
    div.textContent = text;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function responder(msg) {
    msg = msg.toLowerCase();
    for (const chave in respostas) {
      if (msg.includes(chave)) {
        return respostas[chave];
      }
    }
    return respostas.default;
  }

  if (chatSend && chatInput) {
    chatSend.addEventListener("click", () => {
      const texto = chatInput.value.trim();
      if (!texto) return;

      addMessage(texto, "user");
      chatInput.value = "";

      setTimeout(() => {
        addMessage(responder(texto), "bot");
      }, 500);
    });

    chatInput.addEventListener("keypress", e => {
      if (e.key === "Enter") chatSend.click();
    });
  }

  // ===== MENU DROPDOWN DO USUÁRIO (CORRIGIDO) =====
  const userAvatar = document.querySelector('.user-avatar');
  const userDropdown = document.getElementById('userDropdown');

  if (userAvatar && userDropdown) {
    userAvatar.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle('show');
    });

    // Fechar ao clicar fora
    document.addEventListener('click', (e) => {
      if (!userAvatar.contains(e.target) && !userDropdown.contains(e.target)) {
        userDropdown.classList.remove('show');
      }
    });

    // Impede que clique dentro feche o menu
    userDropdown.addEventListener('click', (e) => {
      e.stopPropagation();
    });
  }

  // ===== SIDEBAR =====
  const sidebarOverlay = document.getElementById("sidebar-overlay");
  
  if (sidebarOverlay) {
    sidebarOverlay.addEventListener("click", function () {
      const sidebar = document.getElementById("sidebar");
      if (sidebar) {
        sidebar.classList.remove("open");
      }
      this.classList.remove("show");
    });
  }
});

// Função global para toggle da sidebar
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");

  if (sidebar && overlay) {
    const opened = sidebar.classList.contains("open");

    if (opened) {
      sidebar.classList.remove("open");
      overlay.classList.remove("show");
    } else {
      sidebar.classList.add("open");
      overlay.classList.add("show");
    }
  }
}