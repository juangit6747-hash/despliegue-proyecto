/**
 * fixes_sidebar_tooltips.js
 * 1. Sincroniza margin-left del main-content al colapsar sidebar
 * 2. Agrega data-tooltip a los nav-links del sidebar
 * 3. Deshabilita el drag del chatbot
 * 
 * Agregar en base.html justo antes de </body>:
 * <script src="{% static 'js/fixes_sidebar_tooltips.js' %}"></script>
 */
document.addEventListener('DOMContentLoaded', function () {

  /* ── 1. Tooltips automáticos en sidebar ── */
  var navLinks = document.querySelectorAll('#sidebar .nav-link, #sidebar .nav-parent');
  navLinks.forEach(function (link) {
    var labelEl = link.querySelector('.nav-label');
    if (labelEl && !link.getAttribute('data-tooltip')) {
      link.setAttribute('data-tooltip', labelEl.textContent.trim());
    }
  });

  /* ── 2. Sincronizar main-content con sidebar ── */
  var sidebar     = document.getElementById('sidebar');
  var mainContent = document.getElementById('main-content');
  var topbar      = document.querySelector('.topbar');
  var toggleBtn   = document.getElementById('toggle-btn');

  function syncLayout() {
    if (!sidebar || !mainContent) return;
    var isCollapsed = sidebar.classList.contains('collapsed');
    var w = isCollapsed ? '60px' : '255px';
    mainContent.style.marginLeft = w;
    if (topbar) topbar.style.left = w;
  }

  // Sincronizar al cargar
  syncLayout();

  // Sincronizar al hacer clic en el toggle
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      // Esperar a que termine la transición CSS
      setTimeout(syncLayout, 50);
    });
  }

  /* ── 3. Chatbot estático — deshabilitar drag ── */
  var chatBtn = document.getElementById('chat-btn');
  if (chatBtn) {
    // Quitar event listeners de drag clonando el nodo
    // Solo necesitamos mantener el onclick (toggleChat)
    chatBtn.style.transform = 'none';
    chatBtn.style.cursor    = 'pointer';

    // Bloquear mousedown para drag
    chatBtn.addEventListener('mousedown', function (e) {
      e.stopImmediatePropagation();
    }, true);
  }

});
