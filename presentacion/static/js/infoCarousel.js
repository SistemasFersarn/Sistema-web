document.addEventListener('DOMContentLoaded', function () {
    const carousel = document.querySelector('.info-carousel');
    const cards = document.querySelectorAll('.info-card');
    let currentIndex = 0;
  
    function slideCarousel() {
      currentIndex = (currentIndex + 1) % cards.length;
      carousel.style.transform = `translateX(-${currentIndex * 100}%)`;
    }
  
    setInterval(slideCarousel, 3000); // Cambia cada 3 segundos
  });
  
  const interestCarousel = document.querySelector('.interest-carousel');

function autoScrollCarousel() {
  const scrollAmount = 1; // Cantidad de desplazamiento en píxeles por intervalo
  const maxScrollLeft = interestCarousel.scrollWidth - interestCarousel.clientWidth;
  let direction = 1; // Dirección del desplazamiento (1: derecha, -1: izquierda)
  let isPaused = false; // Indica si el desplazamiento está pausado
  let scrollInterval;

  function startScrolling() {
    scrollInterval = setInterval(() => {
      if (!isPaused) {
        interestCarousel.scrollLeft += scrollAmount * direction;

        // Cambiar dirección al llegar al final o al principio
        if (interestCarousel.scrollLeft >= maxScrollLeft) {
          direction = -1; // Cambia hacia la izquierda
        } else if (interestCarousel.scrollLeft <= 0) {
          direction = 1; // Cambia hacia la derecha
        }
      }
    }, 30);
  }

  function stopScrolling() {
    clearInterval(scrollInterval);
  }

  // Detectar interacción del usuario
  interestCarousel.addEventListener('mousedown', () => {
    isPaused = true; // Pausa el desplazamiento automático
    stopScrolling();
  });

  interestCarousel.addEventListener('mouseup', () => {
    isPaused = false; // Reanuda el desplazamiento automático
    startScrolling();
  });

  interestCarousel.addEventListener('mouseleave', () => {
    isPaused = false; // Reanuda si el ratón sale del área
    startScrolling();
  });

  // Iniciar el desplazamiento automático al cargar
  startScrolling();
}

// Llama a la función para iniciar el desplazamiento automático
autoScrollCarousel();
