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
