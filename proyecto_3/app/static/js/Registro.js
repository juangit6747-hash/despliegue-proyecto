/**
 * registro.js — Módulo de Registro
 * (Renombrado de Registro.js → registro.js para consistencia kebab-case)
 * Encapsulado en IIFE; no expone globals.
 */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    // ── Toggle contraseña ─────────────────────────────────────────
    function setupToggle(toggleId, inputId, iconId) {
      var btn   = document.getElementById(toggleId);
      var input = document.getElementById(inputId);
      var icon  = document.getElementById(iconId);
      if (btn && input && icon) {
        btn.addEventListener('click', function () {
          var tipo = input.type === 'password' ? 'text' : 'password';
          input.type = tipo;
          icon.classList.toggle('fa-eye',       tipo === 'password');
          icon.classList.toggle('fa-eye-slash', tipo === 'text');
        });
      }
    }
    setupToggle('togglePassword1', 'id_contrasena',          'eyeIcon1');
    setupToggle('togglePassword2', 'id_confirmar_contrasena','eyeIcon2');

    // ── Nombre: solo letras y espacios ────────────────────────────
    var inputNombre = document.getElementById('id_nombre');
    if (inputNombre) {
      inputNombre.addEventListener('keypress', function (e) {
        if (e.key.length > 1) return;
        if (!/^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]$/.test(e.key)) e.preventDefault();
      });
      inputNombre.addEventListener('paste', function (e) {
        var texto = (e.clipboardData || window.clipboardData).getData('text');
        if (!/^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$/.test(texto)) e.preventDefault();
      });
    }

    // ── Usuario: solo letras, números y guión bajo ────────────────
    var inputUsuario = document.getElementById('id_usuario');
    if (inputUsuario) {
      inputUsuario.addEventListener('keypress', function (e) {
        if (e.key.length > 1) return;
        if (!/^[a-zA-Z0-9_]$/.test(e.key)) e.preventDefault();
      });
      inputUsuario.addEventListener('paste', function (e) {
        var texto = (e.clipboardData || window.clipboardData).getData('text');
        if (!/^[a-zA-Z0-9_]+$/.test(texto)) e.preventDefault();
      });
    }

    // ── Indicador de fortaleza de contraseña ──────────────────────
    var inputPass = document.getElementById('id_contrasena');
    if (inputPass) {
      inputPass.addEventListener('input', function () {
        var val   = this.value;
        var barra = document.getElementById('fortaleza_bar');
        var fill  = document.getElementById('fortaleza_fill');
        var texto = document.getElementById('fortaleza_texto');

        if (!barra || !fill || !texto) return;

        if (val.length === 0) { barra.style.display = 'none'; return; }
        barra.style.display = 'block';

        var puntos = 0;
        if (val.length >= 8)          puntos++;
        if (/[A-Z]/.test(val))        puntos++;
        if (/[0-9]/.test(val))        puntos++;
        if (/[^a-zA-Z0-9]/.test(val)) puntos++;

        var pct    = ['25%', '50%', '75%', '100%'][puntos - 1] || '10%';
        var color  = ['#dc3545', '#fd7e14', '#ffc107', '#198754'][puntos - 1] || '#dc3545';
        var labels = ['Muy débil', 'Débil', 'Buena', 'Fuerte'];

        fill.style.width           = pct;
        fill.style.backgroundColor = color;
        texto.textContent          = labels[puntos - 1] || 'Muy débil';
        texto.style.color          = color;
      });
    }

    // ── Helpers de errores ────────────────────────────────────────
    function mostrarErr(id, msg) {
      var el = document.getElementById(id);
      if (el) { el.textContent = msg; el.style.display = 'block'; }
    }
    function limpiarErr(id) {
      var el = document.getElementById(id);
      if (el) { el.textContent = ''; el.style.display = 'none'; }
    }

    // ── Validación al enviar ──────────────────────────────────────
    var form = document.getElementById('formRegistro');
    if (form) {
      form.addEventListener('submit', function (e) {
        var valido = true;

        ['err_nombre','err_usuario','err_email','err_contrasena','err_confirmar']
          .forEach(limpiarErr);

        var regexLetras  = /^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$/;
        var regexUsuario = /^[a-zA-Z0-9_]+$/;
        var regexEmail   = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;

        // Nombre
        var nombre = document.getElementById('id_nombre').value.trim();
        if (!nombre) {
          mostrarErr('err_nombre', 'El nombre es obligatorio.'); valido = false;
        } else if (!regexLetras.test(nombre)) {
          mostrarErr('err_nombre', 'El nombre solo puede contener letras y espacios.'); valido = false;
        } else if (nombre.length < 3) {
          mostrarErr('err_nombre', 'El nombre debe tener al menos 3 caracteres.'); valido = false;
        }

        // Usuario
        var usuario = document.getElementById('id_usuario').value.trim();
        if (!usuario) {
          mostrarErr('err_usuario', 'El usuario es obligatorio.'); valido = false;
        } else if (!regexUsuario.test(usuario)) {
          mostrarErr('err_usuario', 'Solo se permiten letras, números y guión bajo (_).'); valido = false;
        } else if (usuario.length < 3) {
          mostrarErr('err_usuario', 'El usuario debe tener al menos 3 caracteres.'); valido = false;
        }

        // Email
        var email = document.getElementById('id_email').value.trim();
        if (!email) {
          mostrarErr('err_email', 'El correo electrónico es obligatorio.'); valido = false;
        } else if (!regexEmail.test(email)) {
          mostrarErr('err_email', 'Ingrese un correo válido (ejemplo: admin@empresa.com).'); valido = false;
        }

        // Contraseña
        var pass = document.getElementById('id_contrasena').value;
        if (!pass) {
          mostrarErr('err_contrasena', 'La contraseña es obligatoria.'); valido = false;
        } else if (pass.length < 8) {
          mostrarErr('err_contrasena', 'La contraseña debe tener al menos 8 caracteres.'); valido = false;
        } else if (!/[A-Z]/.test(pass)) {
          mostrarErr('err_contrasena', 'La contraseña debe contener al menos una mayúscula.'); valido = false;
        } else if (!/[0-9]/.test(pass)) {
          mostrarErr('err_contrasena', 'La contraseña debe contener al menos un número.'); valido = false;
        }

        // Confirmar
        var confirmar = document.getElementById('id_confirmar_contrasena').value;
        if (!confirmar) {
          mostrarErr('err_confirmar', 'Confirma la contraseña.'); valido = false;
        } else if (confirmar !== pass) {
          mostrarErr('err_confirmar', 'Las contraseñas no coinciden.'); valido = false;
        }

        if (!valido) e.preventDefault();
      });
    }

  });

})();
