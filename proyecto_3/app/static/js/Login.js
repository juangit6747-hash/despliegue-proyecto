/**
 * login.js — Módulo de Login
 * (Renombrado de Login.js → login.js para consistencia kebab-case)
 * Encapsulado en IIFE; no expone globals.
 */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    // ── Toggle contraseña ─────────────────────────────────────────
    var togglePassword = document.getElementById('togglePassword');
    var passwordInput  = document.getElementById('passwordInput');
    var eyeIcon        = document.getElementById('eyeIcon');

    if (togglePassword && passwordInput && eyeIcon) {
      togglePassword.addEventListener('click', function () {
        var type = passwordInput.type === 'password' ? 'text' : 'password';
        passwordInput.type = type;
        eyeIcon.classList.toggle('fa-eye',       type === 'password');
        eyeIcon.classList.toggle('fa-eye-slash', type === 'text');
      });
    }

    // ── Usuario: solo letras, números y guión bajo ────────────────
    var inputUsername = document.querySelector('input[name="username"]');
    if (inputUsername) {
      inputUsername.addEventListener('keypress', function (e) {
        if (e.key.length > 1) return;
        if (!/^[a-zA-Z0-9_]$/.test(e.key)) e.preventDefault();
      });
      inputUsername.addEventListener('paste', function (e) {
        var texto = (e.clipboardData || window.clipboardData).getData('text');
        if (!/^[a-zA-Z0-9_]+$/.test(texto)) e.preventDefault();
      });
    }

  });

})();
