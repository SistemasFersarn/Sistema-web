const carouselContainer = document.querySelector('.carousel-container');
const cards = Array.from(document.querySelectorAll('.agency-card'));
const leftBtn = document.querySelector('.left-btn');
const rightBtn = document.querySelector('.right-btn');
let currentIndex = 0;
let interval;
const offset = 0; // Sin desplazamiento inicial para resaltar la tarjeta correcta

// Calcula el desplazamiento para el carrusel
// Calcula el desplazamiento necesario para centrar la tarjeta activa
const calculateOffsetX = () => {
  const containerWidth = carouselContainer.offsetWidth;
  const cardWidth = cards[0].offsetWidth;
  const gap = 21; // Ancho del espacio entre tarjetas
  const totalCardWidth = cardWidth + gap;

  // Centra la tarjeta activa
  return -(currentIndex * totalCardWidth) + (containerWidth / 2 - cardWidth / 2);
};

// Actualiza el carrusel al cambiar la posición
function updateCarousel() {
  cards.forEach(card => card.classList.remove('active'));
  const activeIndex = (currentIndex + offset) % cards.length;
  cards[activeIndex].classList.add('active');

  const offsetX = calculateOffsetX();
  carouselContainer.style.transform = `translateX(${offsetX}px)`;
}

// Inicia el carrusel automático
function startCarousel() {
  if (interval) clearInterval(interval);
  interval = setInterval(() => {
    currentIndex = (currentIndex + 1) % cards.length;
    updateCarousel();
  }, 3000); // Cambia cada 3 segundos
}

// Detiene el carrusel automático
function stopCarousel() {
  clearInterval(interval);
  interval = null;
}

// Muestra el modal con información específica
function showInfo(agency) {
  stopCarousel();

  const modal = document.getElementById('info-modal');
  const modalText = document.getElementById('modal-text');
  const modalImage = document.getElementById('modal-image');

  fetch('/static/data/carrusel.json') // Ruta al archivo JSON
    .then(response => response.json())
    .then(infoContent => {
      const content = infoContent[agency] || { image: '', text: 'No hay información disponible.' };
      modalImage.src = content.image;
      modalText.innerHTML = content.text;
      modal.style.display = 'flex';
    })
    .catch(error => {
      console.error('Error loading agency info:', error);
    });
}


// Cierra el modal y reanuda el carrusel
function closeInfo() {
  const modal = document.getElementById('info-modal');
  modal.style.display = 'none';
  startCarousel();
}

// Función para detectar clic fuera del modal
function closeModalOnClickOutside(event) {
  const modal = document.getElementById('info-modal');
  const modalContent = document.getElementById('modal-content'); // Cambia esto por el ID del contenido dentro del modal
  if (event.target === modal) {
    closeInfo();
  }
}

// Función para detectar la tecla "Esc"
function closeModalOnEsc(event) {
  if (event.key === 'Escape') {
    closeInfo();
  }
}

// Añadir eventos
document.addEventListener('keydown', closeModalOnEsc); // Detecta tecla "Esc"
document.addEventListener('click', closeModalOnClickOutside); // Detecta clic fuera del modal

// Controla los botones de navegación
leftBtn.addEventListener('click', () => {
  currentIndex = currentIndex > 0 ? currentIndex - 1 : cards.length - 1;
  updateCarousel();
  pauseCarouselForButtons();
});

rightBtn.addEventListener('click', () => {
  currentIndex = (currentIndex + 1) % cards.length;
  updateCarousel();
  pauseCarouselForButtons();
});

// Pausa el carrusel unos segundos tras usar los botones
function pauseCarouselForButtons() {
  stopCarousel();
  setTimeout(startCarousel, 1000); // Pausa breve de 1 segundo
}

// Eventos de hover para detener y reanudar el carrusel
cards.forEach(card => {
  card.addEventListener('mouseenter', stopCarousel);
  card.addEventListener('mouseleave', startCarousel);
});

// Swipe para dispositivos táctiles
let startX = 0;

carouselContainer.addEventListener('touchstart', (e) => {
  startX = e.touches[0].clientX;
});

carouselContainer.addEventListener('touchend', (e) => {
  const endX = e.changedTouches[0].clientX;
  const delta = endX - startX;

  if (delta > 50) {
    // Swipe a la derecha
    currentIndex = currentIndex > 0 ? currentIndex - 1 : cards.length - 1;
  } else if (delta < -50) {
    // Swipe a la izquierda
    currentIndex = (currentIndex + 1) % cards.length;
  }
  updateCarousel();
  pauseCarouselForButtons();
});

// Cierra el modal con el botónepe
document.querySelector('.close-btn').addEventListener('click', closeInfo);

// Inicia el carrusel
startCarousel();
updateCarousel(); // Actualiza el carrusel inmediatamente al cargar la página