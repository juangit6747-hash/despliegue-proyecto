/**
 * filtros_realtime.js
 * Sistema de filtros en tiempo real — sin recarga de página
 * Reutilizable en todos los módulos del sistema
 */

(function () {
  'use strict';

  /* ─────────────────────────────────────────────
   * UTILIDADES
   * ───────────────────────────────────────────── */

  /** Normaliza texto: minúsculas + sin tildes */
  function normalizar(str) {
    return (str || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  /** Debounce para inputs de texto */
  function debounce(fn, delay) {
    var timer;
    return function () {
      clearTimeout(timer);
      timer = setTimeout(fn, delay);
    };
  }

  /* ─────────────────────────────────────────────
   * MOTOR DE FILTRADO
   * ───────────────────────────────────────────── */

  /**
   * Filtra las filas de una tabla según los valores actuales
   * de todos los controles de filtro registrados.
   *
   * @param {HTMLElement} container  — elemento con [data-filter-container]
   */
  function aplicarFiltros(container) {
    var tbody   = container.querySelector('tbody');
    var filas   = tbody ? Array.from(tbody.querySelectorAll('tr[data-filter-row]')) : [];
    var inputs  = Array.from(container.querySelectorAll('[data-filter-col]'));
    var counter = container.querySelector('[data-filter-count]');

    // Construir mapa de filtros activos: { colIndex: valorNormalizado }
    var filtros = {};
    inputs.forEach(function (el) {
      var col = el.getAttribute('data-filter-col');
      var val = normalizar(el.value.trim());
      if (val !== '') filtros[col] = val;
    });

    var visibles = 0;

    filas.forEach(function (fila) {
      var mostrar = true;

      Object.keys(filtros).forEach(function (col) {
        var celda = fila.querySelector('[data-col="' + col + '"]');
        if (!celda) { mostrar = false; return; }
        var texto = normalizar(celda.textContent);
        if (texto.indexOf(filtros[col]) === -1) mostrar = false;
      });

      if (mostrar) {
        fila.style.display = '';
        fila.classList.add('filter-visible');
        fila.classList.remove('filter-hidden');
        visibles++;
      } else {
        fila.style.display = 'none';
        fila.classList.add('filter-hidden');
        fila.classList.remove('filter-visible');
      }
    });

    // Fila "sin resultados"
    var noResults = container.querySelector('[data-filter-empty]');
    if (noResults) {
      noResults.style.display = visibles === 0 ? '' : 'none';
    }

    // Contador de resultados
    if (counter) {
      counter.textContent = visibles + ' resultado' + (visibles !== 1 ? 's' : '');
    }

    // Indicador visual de filtros activos
    actualizarEstadoFiltros(container, Object.keys(filtros).length > 0);
  }

  /** Agrega/quita clase CSS cuando hay filtros activos */
  function actualizarEstadoFiltros(container, hayFiltros) {
    var bar = container.querySelector('.rt-filter-bar');
    if (!bar) return;
    if (hayFiltros) {
      bar.classList.add('rt-filter-bar--active');
    } else {
      bar.classList.remove('rt-filter-bar--active');
    }
  }

  /* ─────────────────────────────────────────────
   * INICIALIZACIÓN
   * ───────────────────────────────────────────── */

  function initContainer(container) {
    var inputs = Array.from(container.querySelectorAll('[data-filter-col]'));

    inputs.forEach(function (el) {
      var tag = el.tagName.toLowerCase();

      if (tag === 'select') {
        el.addEventListener('change', function () {
          aplicarFiltros(container);
        });
      } else {
        // input / text / date
        var handler = debounce(function () {
          aplicarFiltros(container);
        }, 220);
        el.addEventListener('input', handler);
        el.addEventListener('keyup', handler);
      }
    });

    // Botón limpiar
    var btnLimpiar = container.querySelector('[data-filter-clear]');
    if (btnLimpiar) {
      btnLimpiar.addEventListener('click', function () {
        inputs.forEach(function (el) {
          if (el.tagName.toLowerCase() === 'select') {
            el.selectedIndex = 0;
          } else {
            el.value = '';
          }
        });
        aplicarFiltros(container);
        // Foco al primer input de texto
        var primerInput = container.querySelector('input[data-filter-col]');
        if (primerInput) primerInput.focus();
      });
    }

    // Aplicar filtros iniciales (por si hay valores pre-cargados)
    aplicarFiltros(container);
  }

  function init() {
    var containers = Array.from(
      document.querySelectorAll('[data-filter-container]')
    );
    containers.forEach(initContainer);
  }

  /* ─────────────────────────────────────────────
   * ARRANQUE
   * ───────────────────────────────────────────── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
