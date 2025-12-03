document.addEventListener('DOMContentLoaded', () => {
  // ===== CARROSSEL =====
  const slidesContainer = document.querySelector('.slides');
  const allSlides = document.querySelectorAll('.slide');
  const prev = document.querySelector('.prev');
  const next = document.querySelector('.next');
  const dotsContainer = document.querySelector('.dots');

  let currentSlide = 0;

  if (slidesContainer && allSlides.length > 0) {
    // ✅ FILTRAR APENAS SLIDES VÁLIDOS (com imagem e visíveis)
    const slides = Array.from(allSlides).filter(slide => {
      const img = slide.querySelector('img');
      const isVisible = slide.offsetParent !== null;
      return img && img.src && isVisible;
    });

    // ✅ LIMPAR BOLINHAS EXISTENTES (se houver)
    if (dotsContainer) {
      dotsContainer.innerHTML = '';
    }

    // ✅ CRIAR BOLINHAS APENAS PARA SLIDES VÁLIDOS
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
      if (dots[currentSlide]) {
        dots[currentSlide].classList.add('active');
      }
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

    // Auto-play do carrossel
    setInterval(nextSlide, 5000);
  }

 // ===== MODO ESCURO / CLARO - VERSÃO COMPATÍVEL =====
(function() {
  const root = document.documentElement;
  const logo = document.getElementById('site-logo');
  const STORAGE_KEY = 'theme';

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    try { localStorage.setItem(STORAGE_KEY, theme); } catch(e){}

    if (logo) {
      logo.style.transition = 'opacity 0.4s ease';
      logo.style.opacity = '0';
      setTimeout(() => {
        if (logo.dataset) {
          logo.src = theme === 'dark' ? logo.dataset.dark : logo.dataset.light;
        }
        logo.style.opacity = '1';
      }, 200);
    }
  }

  // Inicializa tema (usa 'light' como padrão)
  const savedTheme = (() => {
    try { return localStorage.getItem(STORAGE_KEY) || 'light'; } catch(e){ return 'light'; }
  })();
  applyTheme(savedTheme);

  // Quando DOM pronto, conecta o toggle nas configs
  document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');

    if (!themeToggle) {
      // não encontrou o elemento — nada a fazer
      return;
    }

    // marca estado inicial no toggle (para visual)
    if (savedTheme === 'dark') themeToggle.classList.add('active');
    else themeToggle.classList.remove('active');

    // clique no toggle: sincroniza visual, chama toggleSwitch se existir e aplica tema
    themeToggle.addEventListener('click', (e) => {
      // se já existe função global toggleSwitch (usada pelos outros toggles), reutiliza para manter comportamento uniforme
      if (typeof window.toggleSwitch === 'function') {
        try { window.toggleSwitch(themeToggle); } catch (err) { themeToggle.classList.toggle('active'); }
      } else {
        themeToggle.classList.toggle('active');
      }

      const newTheme = themeToggle.classList.contains('active') ? 'dark' : 'light';
      applyTheme(newTheme);

      // se quiser, aqui poderia enviar um fetch/AJAX para salvar preferência no servidor
    });
  });
})();



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
    // BÁSICO
    "oi": "Olá! Como posso ajudar hoje? 😊",
    "ola": "Olá! Como posso ajudar hoje? 😊",
    "bom dia": "Bom dia! Como posso ajudar? ☀️",
    "boa tarde": "Boa tarde! 😊 Em que posso ajudar?",
    "boa noite": "Boa noite! 🌙 Como posso ajudar?",

    // PRODUTOS
    "preço": "Todos os preços estão listados diretamente na página dos produtos.",
    "tamanho": "As opções de tamanho aparecem dentro da página do produto, logo abaixo do nome.",
    "estoque": "O estoque é atualizado automaticamente na página do produto.",
    "material": "Os materiais de cada produto estão descritos na página dele.",
    "garantia": "Nossos produtos possuem garantia legal de 90 dias.",

    // PAGAMENTO
    "pagamento": "Aceitamos PIX, cartão de crédito e boleto.",
    "parcelar": "Sim! Você pode parcelar no cartão em até 12x.",
    "pix": "Pagando via PIX a confirmação ocorre na hora! 🔥",

    // ENTREGA / FRETE
    "entrega": "Realizamos entregas em todo o Brasil. Qual sua cidade?",
    "frete": "O frete é grátis em compras acima de R$129,90 para Santa Catarina.",
    "prazo": "O prazo de entrega aparece ao digitar seu CEP no carrinho.",
    "rastreamento": "Você receberá o código de rastreio por e-mail assim que o pedido for enviado.",
    "rastreio": "Para rastrear seu pedido, acesse a aba *Meus Pedidos* após fazer login.",

    // PEDIDOS
    "pedido": "Para consultar seu pedido, acesse a aba Meus Pedidos no menu superior.",
    "status": "O status pode ser consultado em Meus Pedidos após o login.",
    "acompanhar": "Você pode acompanhar seu pedido em tempo real através de Meus Pedidos.",
    
    // TROCAS E SUPORTE
    "troca": "Para trocas, consulte nossa Política de Troca no rodapé do site.",
    "devolução": "Você tem até 7 dias após o recebimento para solicitar devolução. Para isto entre em contato com o numero de WhatsApp",
    "fale com atendente": "Certo! Um atendente humano pode assumir. Envie seu e-mail ou WhatsApp.",
    "humano": "Certo! Envie seu nome e WhatsApp e eu transfiro para um atendente humano. 😊",

    // LOJA
    "horário": "Nosso suporte funciona 24 horas via site.",
    "telefone": "No momento o suporte é totalmente online, mas podemos te retornar por WhatsApp.",
    "whatsapp": "Envie seu número que um atendente humano entrará em contato!",

    // PADRÃO
    "default": "Desculpe, não entendi. Pode tentar reformular? 😊"
};


  function addMessage(text, type) {
    const div = document.createElement("div");
    div.classList.add(type === "user" ? "user-message" : "bot-message");
    div.textContent = text;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function responder(msg) {
    msg = msg.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, ""); // remove acentos
  
    // Deixa uma cópia simples sem caracteres especiais
    const cleanMsg = msg.replace(/[^\w\s]/gi, "");
  
    // Procura primeiro por combinações exatas
    for (const chave in respostas) {
      const cleanKey = chave.toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        .replace(/[^\w\s]/gi, "");
  
      if (cleanMsg.includes(cleanKey)) {
        return respostas[chave];
      }
    }
  
    // Se nada casar, devolve a resposta padrão
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