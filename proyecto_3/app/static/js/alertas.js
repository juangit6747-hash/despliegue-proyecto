/**
 * alertas.js — Auto-cierre de alertas Django después de 3 segundos.
 * Solo cierra alertas que NO están dentro de un modal.
 */
(function () {
  'use strict';
  document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
      document.querySelectorAll('.alert').forEach(function (alerta) {
        // Ignorar alertas dentro de modales o del chat
        if (alerta.closest('.modal') || alerta.closest('#chat-window')) return;
        try {
          var bsAlert = bootstrap.Alert.getOrCreateInstance(alerta);
          bsAlert.close();
        } catch (e) {}
      });
    }, 3000);
  });
})();