document.addEventListener('DOMContentLoaded', () => {
    // ===== CARROSSEL =====
    const slidesContainer = document.querySelector('.slides');
    const slides = document.querySelectorAll('.slide');
    const prev = document.querySelector('.prev');
    const next = document.querySelector('.next');
    const dotsContainer = document.querySelector('.dots');
  
    let currentSlide = 0;
  
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
  
    next.addEventListener('click', nextSlide);
    prev.addEventListener('click', prevSlide);
  
    setInterval(nextSlide, 5000);
  
    // ===== MODO ESCURO / CLARO =====
    const toggle = document.querySelector('.theme-btn'); // <---- corrigido aqui
    const root = document.documentElement;
    const savedTheme = localStorage.getItem('theme') || 'light';
  
    // aplica tema salvo
    root.setAttribute('data-theme', savedTheme);
    if (toggle) toggle.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
  
    // alterna tema
    if (toggle) {
      toggle.addEventListener('click', () => {
        const current = root.getAttribute('data-theme');
        const newTheme = current === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        toggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
      });
    }
  });
  document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;
    const toggle = document.getElementById('theme-toggle');
  
    // Função para aplicar o tema (usando data-theme no <html>)
    function applyTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
  
      if (theme === 'dark') {
        body.classList.add('dark');
        if (toggle) toggle.checked = true;
      } else {
        body.classList.remove('dark');
        if (toggle) toggle.checked = false;
      }
    }
  
    // Verifica se o usuário tem tema salvo
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
  
    // Evento de alternância
    if (toggle) {
      toggle.addEventListener('change', () => {
        const newTheme = toggle.checked ? 'dark' : 'light';
        applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
      });
    }
  });
  
  