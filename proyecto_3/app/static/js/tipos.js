/**
 * tipos.js — Validaciones del módulo de Tipos de Producto
 * Namespace: window.App.tipos
 */

(function () {
  'use strict';

  window.App = window.App || {};
  window.App.tipos = {};

  var tiposExistentes = [];

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.list-group-item span').forEach(function (el) {
      tiposExistentes.push(el.textContent.trim().toLowerCase());
    });

    var form = document.querySelector('form');
    if (form) {
      form.addEventListener('submit', function (e) {
        var input = form.querySelector('input[name="nombre_tipo"]');
        var valor = input.value.trim();

        if (valor.length < 2) {
          e.preventDefault();
          App.tipos.mostrarError('⚠ El nombre debe tener al menos 2 letras.');
          input.focus();
          return;
        }
        if (tiposExistentes.includes(valor.toLowerCase())) {
          e.preventDefault();
          App.tipos.mostrarError('⚠ Ya existe un tipo con ese nombre.');
          input.focus();
        }
      });
    }
  });

  App.tipos.bloquearNombre = function (input) {
    var antes  = input.value;
    var limpio = antes.replace(/[^a-zA-ZáéíóúÁÉÍÓÚüÜñÑ ]/g, '');
    limpio = limpio.replace(/ {2,}/g, ' ');
    if (antes !== limpio) {
      input.value = limpio;
      App.tipos.mostrarError('⚠ Solo se permiten letras y espacios.');
    }
  };

  App.tipos.mostrarError = function (msg) {
    var el = document.getElementById('tipo_error');
    if (el) {
      el.textContent = msg;
      el.style.display = 'block';
      clearTimeout(el._timer);
      el._timer = setTimeout(function () { el.style.display = 'none'; }, 3000);
    }
  };

  // ── Retrocompatibilidad ─────────────────────────────────────────
  window.bloquearNombreTipo = App.tipos.bloquearNombre;
  window.mostrarErrorTipo   = App.tipos.mostrarError;

})();
