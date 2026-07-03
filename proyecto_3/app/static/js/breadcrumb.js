/**
 * breadcrumb.js
 * Genera automáticamente el breadcrumb navegable en todos los módulos.
 * También implementa tooltips globales para botones e íconos.
 * 
 * Agregar en base.html:
 * <link rel="stylesheet" href="{% static 'css/breadcrumb.css' %}">
 * <script src="{% static 'js/breadcrumb.js' %}"></script>
 */

(function () {
  'use strict';

  /* ══════════════════════════════════════════════════
     MAPA DE RUTAS → Breadcrumb
  ══════════════════════════════════════════════════ */
  var RUTAS = {
    '/':                    [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }],
    '/productos/':          [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Catálogo', icon: 'fa-folder-open' }, { label: 'Productos', icon: 'fa-boxes-stacked' }],
    '/marcas/':             [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Catálogo', icon: 'fa-folder-open' }, { label: 'Marcas', icon: 'fa-tag' }],
    '/unidades/':           [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Catálogo', icon: 'fa-folder-open' }, { label: 'Unidades', icon: 'fa-ruler' }],
    '/tipos/':              [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Catálogo', icon: 'fa-folder-open' }, { label: 'Tipos', icon: 'fa-layer-group' }],
    '/proveedores/':        [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Catálogo', icon: 'fa-folder-open' }, { label: 'Proveedores', icon: 'fa-truck' }],
    '/clientes/':           [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Operaciones', icon: 'fa-briefcase' }, { label: 'Clientes', icon: 'fa-users' }],
    '/ventas/':             [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Operaciones', icon: 'fa-briefcase' }, { label: 'Ventas', icon: 'fa-cart-shopping' }],
    '/compras/':            [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Operaciones', icon: 'fa-briefcase' }, { label: 'Compras', icon: 'fa-bag-shopping' }],
    '/devoluciones/':       [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Operaciones', icon: 'fa-briefcase' }, { label: 'Devoluciones', icon: 'fa-rotate-left' }],
    '/reportes/':           [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Sistema', icon: 'fa-gears' }, { label: 'Reportes', icon: 'fa-chart-line' }],
    '/backup/':             [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Sistema', icon: 'fa-gears' }, { label: 'Respaldo BD', icon: 'fa-database' }],
    '/usuarios/':           [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Sistema', icon: 'fa-gears' }, { label: 'Usuarios', icon: 'fa-users-gear' }],
    '/notificaciones/':     [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Sistema', icon: 'fa-gears' }, { label: 'Notificaciones', icon: 'fa-bell' }],
    '/ia/':                 [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }, { label: 'Sistema', icon: 'fa-gears' }, { label: 'Asistente IA', icon: 'fa-robot' }],
  };

  function getcrumbs() {
    var path = window.location.pathname;
    // Buscar coincidencia exacta primero
    if (RUTAS[path]) return RUTAS[path];
    // Buscar por prefijo (para rutas con parámetros como /ventas/5/)
    var keys = Object.keys(RUTAS).sort(function(a,b){ return b.length - a.length; });
    for (var i = 0; i < keys.length; i++) {
      if (path.startsWith(keys[i]) && keys[i] !== '/') return RUTAS[keys[i]];
    }
    return [{ label: 'Dashboard', icon: 'fa-gauge-high', url: '/' }];
  }

  function renderBreadcrumb() {
    var crumbs = getcrumbs();
    if (!crumbs || crumbs.length <= 1) return; // No mostrar en dashboard

    var nav = document.createElement('nav');
    nav.className = 'breadcrumb-nav';
    nav.setAttribute('aria-label', 'Ruta de navegación');

    crumbs.forEach(function(crumb, i) {
      var isLast = i === crumbs.length - 1;

      if (i > 0) {
        var sep = document.createElement('span');
        sep.className = 'breadcrumb-separator';
        sep.innerHTML = '<i class="fa-solid fa-chevron-right"></i>';
        nav.appendChild(sep);
      }

      var item = document.createElement('div');
      item.className = 'breadcrumb-item' + (isLast ? ' active' : '');

      if (!isLast && crumb.url) {
        var link = document.createElement('a');
        link.href = crumb.url;
        link.innerHTML = '<i class="fa-solid ' + crumb.icon + '"></i> ' + crumb.label;
        link.setAttribute('title', 'Ir a ' + crumb.label);
        item.appendChild(link);
      } else if (!isLast && !crumb.url) {
        // Sección sin enlace (ej: "Catálogo", "Operaciones")
        item.innerHTML = '<i class="fa-solid ' + crumb.icon + '"></i> ' + crumb.label;
      } else {
        // Último item — activo, no es enlace
        item.innerHTML = '<i class="fa-solid ' + crumb.icon + '"></i> ' + crumb.label;
      }

      nav.appendChild(item);
    });

    // Insertar antes del page-title en el page-header-left
    var target = document.querySelector('.page-header-left');
    if (target) {
      target.insertBefore(nav, target.firstChild);
    } else {
      // Fallback: insertar al inicio del contenido principal
      var main = document.getElementById('main-content-area');
      if (main) main.insertBefore(nav, main.firstChild);
    }
  }

  /* ══════════════════════════════════════════════════
     TOOLTIPS GLOBALES
  ══════════════════════════════════════════════════ */
  function initTooltips() {
    var tooltip = document.createElement('div');
    tooltip.className = 'tooltip-custom';
    document.body.appendChild(tooltip);

    var hideTimer = null;

    function showTooltip(e) {
      var el = e.currentTarget;
      var text = el.getAttribute('data-tip') || el.getAttribute('title') || el.getAttribute('aria-label');
      if (!text || text.trim() === '') return;

      // Quitar title para evitar tooltip nativo del navegador
      if (el.getAttribute('title')) {
        el.setAttribute('data-tip', el.getAttribute('title'));
        el.removeAttribute('title');
      }

      clearTimeout(hideTimer);
      tooltip.textContent = text;
      tooltip.classList.add('visible');

      // Posicionar
      var rect = el.getBoundingClientRect();
      var tw = tooltip.offsetWidth;
      var left = rect.left + rect.width / 2 - tw / 2;
      var top  = rect.top - tooltip.offsetHeight - 8;

      // Evitar salir de pantalla
      if (left < 8) left = 8;
      if (left + tw > window.innerWidth - 8) left = window.innerWidth - tw - 8;
      if (top < 8) top = rect.bottom + 8;

      tooltip.style.left = left + 'px';
      tooltip.style.top  = top  + 'px';
    }

    function hideTooltip() {
      hideTimer = setTimeout(function() {
        tooltip.classList.remove('visible');
      }, 100);
    }

    // Aplicar a todos los elementos con title, aria-label o data-tip
    function attachTooltips(root) {
      var els = (root || document).querySelectorAll(
        'button[title], a[title], [aria-label]:not(input):not(select):not(main):not(nav):not(div[role="dialog"]):not(div[role="log"]), [data-tip]'
      );
      els.forEach(function(el) {
        if (el._tooltipAttached) return;
        el._tooltipAttached = true;
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
        el.addEventListener('focus',      showTooltip);
        el.addEventListener('blur',       hideTooltip);
      });
    }

    // Ejecutar al cargar y observar cambios del DOM (para modales que se abren dinámicamente)
    attachTooltips(document);
    var observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(m) {
        m.addedNodes.forEach(function(node) {
          if (node.nodeType === 1) attachTooltips(node);
        });
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  /* ══════════════════════════════════════════════════
     INIT
  ══════════════════════════════════════════════════ */
  document.addEventListener('DOMContentLoaded', function () {
    renderBreadcrumb();
    initTooltips();
  });

})();
