/* animaciones.js - Sistema global de animaciones */

document.addEventListener("DOMContentLoaded", () => {
  const observerOptions = {
    threshold: 0.01,
    rootMargin: "0px 0px 0px 0px"
  };

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-active');
        obs.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll(
    '.animate-fade-up, .animate-fade-in, .animate-slide-left, .animate-slide-right'
  ).forEach(el => observer.observe(el));

  const staggerObserver = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.querySelectorAll('.animate-item').forEach((item, i) => {
          item.style.transitionDelay = `${i * 0.05}s`;
          void item.offsetWidth;
        });
        entry.target.classList.add('animate-active');
        obs.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('.animate-stagger').forEach(c => staggerObserver.observe(c));
});