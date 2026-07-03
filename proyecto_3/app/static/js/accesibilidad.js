/**
 * accesibilidad.js — Panel de accesibilidad flotante
 * Persiste preferencias en localStorage
 */
(function () {
  'use strict';

  var KEY = 'acc_prefs';
  var MIN_FONT = 12, MAX_FONT = 22, STEP = 2;
  var ROOT = document.documentElement;
  var baseFontSize = parseInt(getComputedStyle(ROOT).fontSize) || 16;

  // ── Cargar preferencias ──
  function loadPrefs() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch(e) { return {}; }
  }

  function savePrefs(prefs) {
    try { localStorage.setItem(KEY, JSON.stringify(prefs)); } catch(e) {}
  }

  // ── Aplicar preferencias ──
  function applyPrefs(prefs) {
    var body = document.body;

    // Tamaño de texto
    var size = prefs.fontSize || 0;
    ROOT.style.fontSize = size ? (baseFontSize + size) + 'px' : '';
    var display = document.getElementById('acc-font-display');
    if (display) display.textContent = size === 0 ? 'Normal' : (size > 0 ? '+' + size : size) + 'px';

    // Modos
    body.classList.toggle('acc-high-contrast',   !!prefs.highContrast);
    body.classList.toggle('acc-dyslexia',         !!prefs.dyslexia);
    body.classList.toggle('acc-no-animations',    !!prefs.noAnimations);
    body.classList.toggle('acc-underline-links',  !!prefs.underlineLinks);
    body.classList.toggle('acc-big-cursor',       !!prefs.bigCursor);

    // Sincronizar toggles
    syncToggle('acc-toggle-contrast',    !!prefs.highContrast);
    syncToggle('acc-toggle-dyslexia',    !!prefs.dyslexia);
    syncToggle('acc-toggle-animations',  !!prefs.noAnimations);
    syncToggle('acc-toggle-links',       !!prefs.underlineLinks);
    syncToggle('acc-toggle-cursor',      !!prefs.bigCursor);
  }

  function syncToggle(id, val) {
    var el = document.getElementById(id);
    if (el) el.checked = val;
  }

  // ── HTML del panel ──
  function buildPanel() {
    // Botón
    var btn = document.createElement('button');
    btn.id = 'acc-btn';
    btn.title = 'Opciones de accesibilidad';
    btn.setAttribute('aria-label', 'Abrir panel de accesibilidad');
    btn.innerHTML = '<i class="fa-solid fa-universal-access"></i>';
    document.body.appendChild(btn);

    // Panel
    var panel = document.createElement('div');
    panel.id = 'acc-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Panel de accesibilidad');
    panel.innerHTML = `
      <div class="acc-header">
        <div class="acc-header-title">
          <i class="fa-solid fa-universal-access"></i> Accesibilidad
        </div>
        <button class="acc-close" id="acc-close-btn" aria-label="Cerrar panel">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      <div class="acc-body">

        <!-- Tamaño de texto -->
        <div class="acc-group">
          <div class="acc-label">Tamaño de texto</div>
          <div class="acc-font-controls">
            <button class="acc-font-btn" id="acc-font-dec" aria-label="Reducir texto">A-</button>
            <div class="acc-font-display" id="acc-font-display">Normal</div>
            <button class="acc-font-btn" id="acc-font-inc" aria-label="Aumentar texto">A+</button>
          </div>
        </div>

        <!-- Opciones de visualización -->
        <div class="acc-group">
          <div class="acc-label">Visualización</div>

          <label class="acc-option">
            <div class="acc-option-label">
              <i class="fa-solid fa-circle-half-stroke"></i> Alto contraste
            </div>
            <div class="acc-toggle">
              <input type="checkbox" id="acc-toggle-contrast" aria-label="Alto contraste">
              <span class="acc-toggle-slider"></span>
            </div>
          </label>

          <label class="acc-option">
            <div class="acc-option-label">
              <i class="fa-solid fa-ban"></i> Sin animaciones
            </div>
            <div class="acc-toggle">
              <input type="checkbox" id="acc-toggle-animations" aria-label="Desactivar animaciones">
              <span class="acc-toggle-slider"></span>
            </div>
          </label>

          <label class="acc-option">
            <div class="acc-option-label">
              <i class="fa-solid fa-link"></i> Subrayar enlaces
            </div>
            <div class="acc-toggle">
              <input type="checkbox" id="acc-toggle-links" aria-label="Subrayar enlaces">
              <span class="acc-toggle-slider"></span>
            </div>
          </label>
        </div>

        <!-- Opciones de lectura -->
        <div class="acc-group">
          <div class="acc-label">Lectura</div>

          <label class="acc-option">
            <div class="acc-option-label">
              <i class="fa-solid fa-font"></i> Fuente para dislexia
            </div>
            <div class="acc-toggle">
              <input type="checkbox" id="acc-toggle-dyslexia" aria-label="Fuente para dislexia">
              <span class="acc-toggle-slider"></span>
            </div>
          </label>

          <label class="acc-option">
            <div class="acc-option-label">
              <i class="fa-solid fa-arrow-pointer"></i> Cursor grande
            </div>
            <div class="acc-toggle">
              <input type="checkbox" id="acc-toggle-cursor" aria-label="Cursor grande">
              <span class="acc-toggle-slider"></span>
            </div>
          </label>

          <label class="acc-option">
            <div class="acc-option-label">
              <i class="fa-solid fa-volume-high"></i> Leer texto al pasar
            </div>
            <div class="acc-toggle">
              <input type="checkbox" id="acc-toggle-tts" aria-label="Leer texto al pasar el mouse">
              <span class="acc-toggle-slider"></span>
            </div>
          </label>
        </div>

        <!-- Reset -->
        <button class="acc-reset" id="acc-reset-btn">
          <i class="fa-solid fa-rotate-left"></i> Restablecer todo
        </button>

      </div>
    `;
    document.body.appendChild(panel);
  }

  // ── Inicializar ──
  document.addEventListener('DOMContentLoaded', function () {
    buildPanel();

    var prefs = loadPrefs();
    applyPrefs(prefs);

    var panel = document.getElementById('acc-panel');
    var btn   = document.getElementById('acc-btn');

    // Abrir/cerrar
    btn.addEventListener('click', function () {
      panel.classList.toggle('open');
      btn.setAttribute('aria-expanded', panel.classList.contains('open'));
    });

    document.getElementById('acc-close-btn').addEventListener('click', function () {
      panel.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    });

    // Cerrar al hacer clic fuera
    document.addEventListener('click', function (e) {
      if (!panel.contains(e.target) && e.target !== btn && !btn.contains(e.target)) {
        panel.classList.remove('open');
      }
    });

    // Tamaño de texto
    document.getElementById('acc-font-inc').addEventListener('click', function () {
      var p = loadPrefs();
      p.fontSize = Math.min((p.fontSize || 0) + STEP, MAX_FONT - baseFontSize);
      savePrefs(p); applyPrefs(p);
    });

    document.getElementById('acc-font-dec').addEventListener('click', function () {
      var p = loadPrefs();
      p.fontSize = Math.max((p.fontSize || 0) - STEP, MIN_FONT - baseFontSize);
      savePrefs(p); applyPrefs(p);
    });

    // Toggles
    var toggleMap = {
      'acc-toggle-contrast':   'highContrast',
      'acc-toggle-animations': 'noAnimations',
      'acc-toggle-links':      'underlineLinks',
      'acc-toggle-dyslexia':   'dyslexia',
      'acc-toggle-cursor':     'bigCursor',
      'acc-toggle-tts':        'tts',
    };

    Object.keys(toggleMap).forEach(function (id) {
      var el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('change', function () {
        var p = loadPrefs();
        p[toggleMap[id]] = this.checked;
        savePrefs(p); applyPrefs(p);
        if (id === 'acc-toggle-tts') toggleTTS(this.checked);
      });
    });

    // TTS — leer en voz alta al pasar el mouse
    var ttsActive = false;
    var ttsTimeout = null;

    function toggleTTS(enable) {
      ttsActive = enable;
      if (!enable && window.speechSynthesis) window.speechSynthesis.cancel();
    }

    document.addEventListener('mouseover', function(e) {
      if (!ttsActive || !window.speechSynthesis) return;
      var el = e.target.closest('td, th, .stat-label, .stat-value, .nav-label, h1, h2, h3, p, label, .glass-card-title, .page-title');
      if (!el) return;
      var text = el.textContent.trim().replace(/\s+/g, ' ');
      if (!text || text.length < 2) return;
      clearTimeout(ttsTimeout);
      ttsTimeout = setTimeout(function() {
        window.speechSynthesis.cancel();
        var utt = new SpeechSynthesisUtterance(text);
        utt.lang = 'es-CO';
        utt.rate = 0.95;
        window.speechSynthesis.speak(utt);
      }, 400);
    });

    // Aplicar TTS si estaba activo
    if (prefs.tts) { syncToggle('acc-toggle-tts', true); ttsActive = true; }

    // Reset
    document.getElementById('acc-reset-btn').addEventListener('click', function () {
      savePrefs({});
      applyPrefs({});
      ROOT.style.fontSize = '';
      toggleTTS(false);
    });

    // Cerrar con Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && panel.classList.contains('open')) {
        panel.classList.remove('open');
        btn.focus();
      }
    });
  });
})();
