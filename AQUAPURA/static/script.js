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

  // função para aplicar tema + logo
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

  // aplica tema salvo
  const savedTheme = localStorage.getItem('theme') || 'light';
  applyTheme(savedTheme);

  // alternar tema
  if (toggle) {
    toggle.addEventListener('click', () => {
      const current = root.getAttribute('data-theme');
      const newTheme = current === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);
    });
  }
});

document.addEventListener('DOMContentLoaded', () => {

  const chatContainer = document.getElementById("chat-container");
  const chatOpen = document.getElementById("chat-open");
  const chatClose = document.getElementById("chat-close");
  const chatBody = document.getElementById("chat-body");
  const chatInput = document.getElementById("chat-input");
  const chatSend = document.getElementById("chat-send");

  // Abrir e fechar chat
  chatOpen.addEventListener("click", () => {
      chatContainer.classList.remove("hidden");
  });
  chatClose.addEventListener("click", () => {
      chatContainer.classList.add("hidden");
  });

  // Lista de respostas pré-definidas (você edita como quiser)
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

});

document.addEventListener("DOMContentLoaded", () => {

  const avatar = document.getElementById("userAvatar");
  const dropdown = document.getElementById("userDropdown");

  if (!avatar || !dropdown) return;

  // Abrir / Fechar ao clicar no avatar
  avatar.addEventListener("click", (e) => {
      e.stopPropagation(); 
      dropdown.classList.toggle("show");
  });

  // Fechar ao clicar fora
  document.addEventListener("click", () => {
      dropdown.classList.remove("show");
  });

  // Impede que clique dentro feche o menu
  dropdown.addEventListener("click", (e) => {
      e.stopPropagation();
  });
});
