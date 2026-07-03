/**
 * confirmaciones.js — Diálogos de confirmación globales (SweetAlert2)
 * Namespace: window.App.confirmar
 * Estilo unificado con fondo oscuro y colores del sistema.
 */

(function () {
  'use strict';

  window.App = window.App || {};
  window.App.confirmar = window.App.confirmar || {};

  function _swalEliminar(titulo, html, form) {
    Swal.fire({
      icon: 'warning',
      title: titulo,
      html: html,
      showCancelButton: true,
      confirmButtonText: '<i class="fa-solid fa-trash me-1"></i> Sí, eliminar',
      cancelButtonText: 'Cancelar',
      confirmButtonColor: '#c0392b',
      cancelButtonColor: '#555',
      background: '#0e1420',
      color: '#f0f4ff',
    }).then(function (result) {
      if (result.isConfirmed) form.submit();
    });
  }

  App.confirmar.eliminar = function (nombre, form) {
    _swalEliminar(
      '¿Eliminar elemento?',
      '¿Estás seguro de eliminar <strong>' + nombre + '</strong>?<br><span style="color:#e74c3c;font-size:.88rem;">Esta acción no se puede deshacer.</span>',
      form
    );
  };

  App.confirmar.eliminarMarca = function (nombre, form) {
    _swalEliminar(
      '¿Eliminar marca?',
      '¿Estás seguro de eliminar la marca <strong>' + nombre + '</strong>?<br><span style="color:#e74c3c;font-size:.88rem;">Esta acción no se puede deshacer.</span>',
      form
    );
  };

  App.confirmar.eliminarUnidad = function (nombre, form) {
    _swalEliminar(
      '¿Eliminar unidad?',
      '¿Estás seguro de eliminar la unidad <strong>' + nombre + '</strong>?<br><span style="color:#e74c3c;font-size:.88rem;">Esta acción no se puede deshacer.</span>',
      form
    );
  };

  App.confirmar.eliminarTipo = function (nombre, form) {
    _swalEliminar(
      '¿Eliminar tipo?',
      '¿Estás seguro de eliminar el tipo <strong>' + nombre + '</strong>?<br><span style="color:#e74c3c;font-size:.88rem;">Esta acción no se puede deshacer.</span>',
      form
    );
  };

  // Retrocompatibilidad global
  window.confirmarEliminar = App.confirmar.eliminar;

})();
