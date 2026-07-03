/**
 * marcas.js — Validaciones del módulo de Marcas
 * Namespace: window.App.marcas
 * confirmarEliminar → delegado a App.confirmar.eliminarMarca (confirmaciones.js)
 */

(function () {
  'use strict';

  window.App = window.App || {};
  window.App.marcas = {};

  var marcasExistentes = [];

  document.addEventListener('DOMContentLoaded', function () {
    // Recolectar marcas existentes del listado
    document.querySelectorAll('.list-group-item .fw-semibold').forEach(function (el) {
      marcasExistentes.push(el.textContent.trim().toLowerCase());
    });

    var form = document.querySelector('form');
    if (form) {
      form.addEventListener('submit', function (e) {
        var input = form.querySelector('input[name="nombreMarca"]');
        var valor = input.value.trim();

        if (valor.length < 2) {
          e.preventDefault();
          App.marcas.mostrarError('⚠ El nombre debe tener al menos 2 letras.');
          input.focus();
          return;
        }
        if (marcasExistentes.includes(valor.toLowerCase())) {
          e.preventDefault();
          App.marcas.mostrarError('⚠ Ya existe una marca con ese nombre.');
          input.focus();
        }
      });
    }
  });

  App.marcas.bloquearNombre = function (input) {
    var limpio = input.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚüÜñÑ ]/g, '');
    limpio = limpio.replace(/ {2,}/g, ' ');
    if (input.value !== limpio) {
      input.value = limpio;
      App.marcas.mostrarError('⚠ Solo se permiten letras, sin números ni caracteres especiales.');
    }
  };

  App.marcas.mostrarError = function (msg) {
    var el = document.getElementById('marca_error');
    if (el) {
      el.textContent = msg;
      el.style.display = 'block';
      clearTimeout(el._timer);
      el._timer = setTimeout(function () { el.style.display = 'none'; }, 3000);
    }
  };

  // ── Retrocompatibilidad ─────────────────────────────────────────
  // Expone las funciones que los templates llaman directamente.
  // Migrar templates a App.marcas.bloquearNombre en la siguiente iteración.
  window.bloquearNombreMarca = App.marcas.bloquearNombre;
  window.mostrarErrorMarca   = App.marcas.mostrarError;
  // confirmarEliminar de marcas → usa el centralizado en confirmaciones.js
  // En el template: onclick="App.confirmar.eliminarMarca(...)"

})();
