document.addEventListener('DOMContentLoaded', () => {
  // ===== CARROSSEL =====
  const slidesContainer = document.querySelector('.slides');
  const allSlides = document.querySelectorAll('.slide');
  const prev = document.querySelector('.prev');
  const next = document.querySelector('.next');
  const dotsContainer = document.querySelector('.dots');

  let currentSlide = 0;

  if (slidesContainer && allSlides.length > 0) {
    const slides = Array.from(allSlides).filter(slide => {
      const img = slide.querySelector('img');
      const isVisible = slide.offsetParent !== null;
      return img && img.src && isVisible;
    });

    if (dotsContainer) {
      dotsContainer.innerHTML = '';
    }

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

    setInterval(nextSlide, 5000);
  }

 // ===== MODO ESCURO / CLARO =====
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

  const savedTheme = (() => {
    try { return localStorage.getItem(STORAGE_KEY) || 'light'; } catch(e){ return 'light'; }
  })();
  applyTheme(savedTheme);

  document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');

    if (!themeToggle) {
      return;
    }

    if (savedTheme === 'dark') themeToggle.classList.add('active');
    else themeToggle.classList.remove('active');

    themeToggle.addEventListener('click', (e) => {
      if (typeof window.toggleSwitch === 'function') {
        try { window.toggleSwitch(themeToggle); } catch (err) { themeToggle.classList.toggle('active'); }
      } else {
        themeToggle.classList.toggle('active');
      }

      const newTheme = themeToggle.classList.contains('active') ? 'dark' : 'light';
      applyTheme(newTheme);
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
    "oi": "Olá! Como posso ajudar hoje? 😊",
    "ola": "Olá! Como posso ajudar hoje? 😊",
    "bom dia": "Bom dia! Como posso ajudar? ☀️",
    "boa tarde": "Boa tarde! 😊 Em que posso ajudar?",
    "boa noite": "Boa noite! 🌙 Como posso ajudar?",
    "preço": "Todos os preços estão listados diretamente na página dos produtos.",
    "tamanho": "As opções de tamanho aparecem dentro da página do produto.",
    "estoque": "O estoque é atualizado automaticamente na página do produto.",
    "material": "Os materiais de cada produto estão descritos na página dele.",
    "garantia": "Nossos produtos possuem garantia legal de 90 dias.",
    "pagamento": "Aceitamos PIX, cartão de crédito e boleto.",
    "parcelar": "Sim! Você pode parcelar no cartão em até 12x.",
    "pix": "Pagando via PIX a confirmação ocorre na hora! 🔥",
    "entrega": "Realizamos entregas em todo o Brasil. Qual sua cidade?",
    "frete": "O frete é grátis em compras acima de R$129,90 para Santa Catarina.",
    "prazo": "O prazo de entrega aparece ao digitar seu CEP no carrinho.",
    "rastreamento": "Você receberá o código de rastreio por e-mail.",
    "rastreio": "Para rastrear seu pedido, acesse a aba *Meus Pedidos* após fazer login.",
    "pedido": "Para consultar seu pedido, acesse a aba Meus Pedidos no menu superior.",
    "status": "O status pode ser consultado em Meus Pedidos após o login.",
    "acompanhar": "Você pode acompanhar seu pedido em tempo real através de Meus Pedidos.",
    "troca": "Para trocas, consulte nossa Política de Troca no rodapé do site.",
    "devolução": "Você tem até 7 dias após o recebimento para solicitar devolução.",
    "horário": "Nosso suporte funciona 24 horas via site.",
    "telefone": "No momento o suporte é totalmente online, mas podemos te retornar por WhatsApp.",
    "whatsapp": "Envie seu número que um atendente humano entrará em contato!",
    "default": "Desculpe, não entendi. Pode tentar reformular? 😊"
  };

  function addMessage(text, type) {
    const div = document.createElement("div");
    div.classList.add(type === "user" ? "user-message" : "bot-message");
    div.textContent = text;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  // ===== NOVA FUNÇÃO: ADICIONAR BOTÃO DE ATENDENTE =====
  function addButtonAtendente() {
    const div = document.createElement("div");
    div.classList.add("bot-message");
    div.innerHTML = `
      <p>Entendi! Vou te conectar com um atendente humano.</p>
      <button onclick="solicitarAtendente()" style="
        background: linear-gradient(135deg, #0891b2, #0e7490);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        margin-top: 10px;
        transition: all 0.3s ease;
      " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
        💬 Falar com Atendente
      </button>
    `;
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function responder(msg) {
    msg = msg.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const cleanMsg = msg.replace(/[^\w\s]/gi, "");

    // ===== DETECTAR SOLICITAÇÃO DE ATENDENTE =====
    const palavrasAtendente = [
      'atendente', 'humano', 'pessoa', 'falar com alguem', 
      'preciso de ajuda', 'nao entendi', 'quero falar',
      'me ajuda', 'ajuda urgente', 'problema', 'reclamacao'
    ];

    const solicitouAtendente = palavrasAtendente.some(palavra => 
      cleanMsg.includes(palavra.replace(/\s/g, ''))
    );

    if (solicitouAtendente) {
      addButtonAtendente();
      return null; // Não retorna texto, só o botão
    }

    // Respostas automáticas normais
    for (const chave in respostas) {
      const cleanKey = chave.toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        .replace(/[^\w\s]/gi, "");

      if (cleanMsg.includes(cleanKey)) {
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
        const resposta = responder(texto);
        if (resposta) {
          addMessage(resposta, "bot");
        }
      }, 500);
    });

    chatInput.addEventListener("keypress", e => {
      if (e.key === "Enter") chatSend.click();
    });
  }

  // ===== MENU DROPDOWN DO USUÁRIO =====
  const userAvatar = document.querySelector('.user-avatar');
  const userDropdown = document.getElementById('userDropdown');

  if (userAvatar && userDropdown) {
    userAvatar.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!userAvatar.contains(e.target) && !userDropdown.contains(e.target)) {
        userDropdown.classList.remove('show');
      }
    });

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

// ===== FUNÇÃO GLOBAL: SOLICITAR ATENDENTE =====
window.solicitarAtendente = async function() {
  try {
    const response = await fetch('/api/solicitar-atendente', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (data.sucesso) {
      // Fechar chat bot
      document.getElementById('chat-container').classList.add('hidden');
      
      // Redirecionar para página de chat
      window.location.href = `/chat/${data.chat_id}`;
    } else {
      alert(data.erro || 'Erro ao solicitar atendente. Tente novamente.');
    }
  } catch (error) {
    console.error('Erro:', error);
    alert('Erro ao conectar com o servidor. Tente novamente.');
  }
};

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