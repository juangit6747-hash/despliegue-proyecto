/**
 * escaner.js — Escáner profesional con ZXing-js
 * Modo inventario rápido, historial, barra de stock, sonidos
 */
(function () {
  'use strict';

  // Funciona tanto en productos (btnAbrirEscaner) como en ventas (btnEscanerVenta)
  if (!document.getElementById('btnAbrirEscaner') && !document.getElementById('btnEscanerVenta')) return;

  // ── Estado ──
  var codeReader = null;
  var streaming  = false;
  var lastCode   = '';
  var lastTime   = 0;
  var DEBOUNCE   = 2000;
  var modoInventario = false;
  var modoVenta      = false;   // true cuando se abre desde ventas
  var pendientes = [];   // lista de ajustes en modo inventario
  var historial  = [];   // últimos 10 escaneos
  var sesionActualizados = 0;
  var sesionNuevos       = 0;

  // ── Elementos ──
  var modalEl    = document.getElementById('modalEscaner');
  var btnCamara  = document.getElementById('escaner-btn-camara');
  var btnImagen  = document.getElementById('escaner-btn-imagen');
  var inputImg   = document.getElementById('escaner-input-imagen');
  var areaLector = document.getElementById('escaner-area-lector');
  var statusEl   = document.getElementById('escaner-status');
  var resultadoEl= document.getElementById('escaner-resultado');
  var historialEl= document.getElementById('escaner-historial');
  var contadorEl = document.getElementById('escaner-contador-sesion');
  var modalBS    = null;

  // ── Audio ──
  function beep(tipo) {
    try {
      var ctx  = new (window.AudioContext || window.webkitAudioContext)();
      var osc  = ctx.createOscillator();
      var gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.value = tipo === 'ok'    ? 880  :
                            tipo === 'nuevo' ? 660  : 330;
      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.3);
    } catch(e) {}
  }

  // ── Abrir modal ──
  var btnAbrirEscaner = document.getElementById('btnAbrirEscaner');
  if (btnAbrirEscaner) {
    btnAbrirEscaner.addEventListener('click', function () {
      modoVenta = false;
      modalBS = bootstrap.Modal.getOrCreateInstance(modalEl);
      modalBS.show();
    });
  }

  // Botón escaner en ventas (modo venta)
  var btnEscanerVenta = document.getElementById('btnEscanerVenta');
  if (btnEscanerVenta) {
    btnEscanerVenta.addEventListener('click', function () {
      modoVenta = true;
      modalBS = bootstrap.Modal.getOrCreateInstance(modalEl);
      modalBS.show();
    });
  }

  modalEl.addEventListener('shown.bs.modal', function () {
    actualizarContadorBtn();
    iniciarCamara();
    // Cambiar título según modo
    var titulo = modalEl.querySelector('.modal-title');
    if (titulo) {
      titulo.innerHTML = modoVenta
        ? '<i class="fa-solid fa-cart-shopping" style="color:var(--c-gold);"></i> Escanear producto para venta'
        : '<i class="fa-solid fa-barcode" style="color:var(--c-info);"></i> Escanear Código de Barras';
    }
    // Ocultar modo inventario en modo venta
    var btnInv = document.getElementById('escaner-btn-modo-inventario');
    if (btnInv) btnInv.style.display = modoVenta ? 'none' : '';
  });

 modalEl.addEventListener('hidden.bs.modal', function () {
    detener();
    resetUI();
    modoInventario = false;
    modoVenta      = false;
    pendientes = [];
    document.querySelectorAll('.modal-backdrop').forEach(function(el){ el.remove(); });
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('overflow');
    document.body.style.removeProperty('padding-right');
  });

  // ── Modo cámara / imagen ──
  btnCamara.addEventListener('click', function () {
    btnCamara.classList.add('active');
    btnImagen.classList.remove('active');
    inputImg.style.display = 'none';
    detener(); resetUI(); iniciarCamara();
  });

  btnImagen.addEventListener('click', function () {
    btnImagen.classList.add('active');
    btnCamara.classList.remove('active');
    detener(); resetUI();
    inputImg.style.display = 'block';
    inputImg.click();
  });

  inputImg.addEventListener('change', function () {
    if (!this.files || !this.files[0]) return;
    leerDesdeImagen(this.files[0]);
    this.value = '';
  });

  // ── Modo inventario rápido ──
  var btnModoInv = document.getElementById('escaner-btn-modo-inventario');
  if (btnModoInv) {
    btnModoInv.addEventListener('click', function () {
      modoInventario = !modoInventario;
      pendientes = [];
      if (modoInventario) {
        btnModoInv.classList.remove('btn-secondary');
        btnModoInv.classList.add('btn-warning');
        btnModoInv.innerHTML = '<i class="fa-solid fa-stop"></i> Salir del modo inventario';
        setStatus('Modo inventario activo — escanea varios productos seguidos', 'info');
        mostrarListaPendientes();
      } else {
        btnModoInv.classList.remove('btn-warning');
        btnModoInv.classList.add('btn-secondary');
        btnModoInv.innerHTML = '<i class="fa-solid fa-boxes-stacked"></i> Modo inventario rapido';
        resetResultado();
        setStatus('', '');
      }
    });
  }

  // ── ZXing cámara ──
  function iniciarCamara() {
    if (streaming) return;
    areaLector.innerHTML = '<video id="escaner-video" style="width:100%;max-height:260px;border-radius:var(--r-md);background:#000;" autoplay muted playsinline></video>';
    setStatus('Apunta la camara al codigo de barras...', 'info');
    try {
      var hints = new Map();
      hints.set(ZXing.DecodeHintType.POSSIBLE_FORMATS, [
        ZXing.BarcodeFormat.EAN_13, ZXing.BarcodeFormat.EAN_8,
        ZXing.BarcodeFormat.CODE_128, ZXing.BarcodeFormat.CODE_39,
        ZXing.BarcodeFormat.UPC_A,  ZXing.BarcodeFormat.UPC_E,
      ]);
      hints.set(ZXing.DecodeHintType.TRY_HARDER, true);
      codeReader = new ZXing.BrowserMultiFormatReader(hints);
      codeReader.decodeFromVideoDevice(null, 'escaner-video', function (result, err) {
        if (!result) return;
        var codigo = result.getText();
        var now    = Date.now();
        if (codigo === lastCode && (now - lastTime) < DEBOUNCE) return;
        lastCode = codigo; lastTime = now;
        setStatus('Codigo detectado: ' + codigo, 'ok');
        procesarCodigo(codigo);
      });
      streaming = true;
    } catch(e) {
      setStatus('No se pudo acceder a la camara. Usa "Subir Imagen".', 'error');
    }
  }

  // ── ZXing imagen ──
  function leerDesdeImagen(file) {
    setStatus('Analizando imagen...', 'info');
    resetResultado();
    areaLector.innerHTML = '';
    var url = URL.createObjectURL(file);
    var img = new Image();
    img.onload = function () {
      areaLector.innerHTML = '<img src="' + url + '" style="width:100%;max-height:240px;object-fit:contain;border-radius:var(--r-md);">';
      try {
        var hints = new Map();
        hints.set(ZXing.DecodeHintType.TRY_HARDER, true);
        new ZXing.BrowserMultiFormatReader(hints).decodeFromImageUrl(url)
          .then(function (result) {
            setStatus('Codigo leido: ' + result.getText(), 'ok');
            procesarCodigo(result.getText());
            URL.revokeObjectURL(url);
          })
          .catch(function () {
            setStatus('No se pudo leer el codigo. Intenta con mejor iluminacion y sin reflejos.', 'error');
            URL.revokeObjectURL(url);
          });
      } catch(e) { setStatus('Error al procesar la imagen.', 'error'); }
    };
    img.src = url;
  }

  function detener() {
    if (codeReader) { try { codeReader.reset(); } catch(e) {} codeReader = null; }
    streaming = false;
  }

  // ── Procesar código ──
  function procesarCodigo(codigo) {
    if (!modoInventario) resetResultado();
    setStatus('Buscando: ' + codigo + '...', 'info');

    fetch('/productos/buscar-escaner/?codigo=' + encodeURIComponent(codigo))
      .then(function(r){ return r.json(); })
      .then(function(data) {
        if (data.estado === 'encontrado') {
          beep('ok');
          if (modoInventario) {
            agregarAPendientes(data);
          } else {
            mostrarEncontrado(data);
          }
          agregarHistorial(data.nombre, codigo, 'encontrado');
        } else {
          beep('nuevo');
          if (!modoInventario) mostrarNoEncontrado(data);
          agregarHistorial('No registrado', codigo, 'nuevo');
          if (modoInventario) {
            setStatus('Producto no registrado: ' + codigo + ' — registralo primero.', 'error');
          }
        }
        renderHistorial();
        actualizarContadorBtn();
      })
      .catch(function() { setStatus('Error de conexion.', 'error'); beep('error'); });
  }

  // ── Mostrar producto encontrado (panel limpio) ──
  function mostrarEncontrado(data) {
    setStatus('', '');
    var pct   = Math.min(100, Math.round((data.stock / 100) * 100));
    var color = data.stock === 0 ? 'var(--c-danger)' :
                data.stock <= 5  ? 'var(--c-gold)'   : 'var(--c-success)';
    var texto = data.stock === 0 ? 'Sin stock' :
                data.stock <= 5  ? 'Stock bajo' : 'Stock OK';
    var badge = data.stock === 0 ? 'badge-danger' :
                data.stock <= 5  ? 'badge-warning' : 'badge-success';

    resultadoEl.innerHTML =
      '<div style="background:var(--bg-card);border:1px solid rgba(39,174,96,0.25);border-radius:var(--r-md);padding:20px;margin-top:12px;">' +
        // Header producto
        '<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">' +
          '<div style="width:46px;height:46px;background:var(--c-success-l);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.3rem;color:var(--c-success);flex-shrink:0;">' +
            '<i class="fa-solid fa-circle-check"></i>' +
          '</div>' +
          '<div style="flex:1;">' +
            '<div style="font-weight:700;font-size:1rem;color:var(--tx-primary);">' + data.nombre + '</div>' +
            '<div style="font-size:.78rem;color:var(--tx-muted);">EAN: ' + data.codigo + '</div>' +
          '</div>' +
          '<span class="badge ' + badge + '" style="font-size:.75rem;">' + texto + '</span>' +
        '</div>' +
        // Barra de stock
        '<div style="margin-bottom:16px;">' +
          '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">' +
            '<span style="font-size:.78rem;font-weight:600;color:var(--tx-secondary);text-transform:uppercase;letter-spacing:.05em;">Stock actual</span>' +
            '<span style="font-family:var(--font-mono);font-weight:800;font-size:1.1rem;color:' + color + ';">' + data.stock + ' uds</span>' +
          '</div>' +
          '<div style="height:8px;background:var(--bd-default);border-radius:8px;overflow:hidden;">' +
            '<div style="height:100%;width:' + Math.max(pct, data.stock > 0 ? 5 : 0) + '%;background:' + color + ';border-radius:8px;transition:width .5s ease;"></div>' +
          '</div>' +
        '</div>' +
        // Control de cantidad
        '<div style="background:var(--bg-glass);border-radius:var(--r-sm);padding:14px;border:1px solid var(--bd-subtle);">' +
          '<div style="font-size:.78rem;font-weight:700;color:var(--tx-secondary);text-transform:uppercase;letter-spacing:.05em;margin-bottom:10px;">Agregar al stock</div>' +
          '<div style="display:flex;align-items:center;gap:8px;">' +
            '<button onclick="escaner_cambiarCantidad(-1)" class="btn btn-secondary btn-sm btn-icon-sq" style="font-size:1rem;font-weight:700;">-</button>' +
            '<input type="number" id="escaner-cantidad" value="1" min="1" max="9999"' +
              ' style="width:70px;padding:8px;background:var(--bg-input);border:1px solid var(--bd-default);border-radius:var(--r-sm);color:var(--tx-primary);font-size:1rem;font-weight:700;text-align:center;">' +
            '<button onclick="escaner_cambiarCantidad(1)" class="btn btn-secondary btn-sm btn-icon-sq" style="font-size:1rem;font-weight:700;">+</button>' +
            (modoVenta
              ? '<button onclick="window.escaner_agregarVenta(' + data.id + ',this)" class="btn btn-warning" style="flex:1;" data-nombre="' + data.nombre.replace(/"/g, '&quot;') + '" data-precio="' + data.precio + '" data-stock="' + data.stock + '"><i class="fa-solid fa-cart-shopping"></i> Agregar a venta</button>'
              : '<button onclick="window.escaner_agregarStock(' + data.id + ')" class="btn btn-success" style="flex:1;"><i class="fa-solid fa-plus"></i> Actualizar stock</button>'
            ) +
          '</div>' +
        '</div>' +
      '</div>';
  }

  // ── Mostrar no encontrado ──
  function mostrarNoEncontrado(data) {
    var infoExtra = '';
    if (data.nombre_sugerido) {
      infoExtra =
        '<div style="background:var(--c-info-l);border:1px solid rgba(41,128,185,0.2);border-radius:var(--r-sm);padding:10px 14px;margin-bottom:12px;font-size:.82rem;">' +
          '<i class="fa-solid fa-lightbulb" style="color:var(--c-info);margin-right:6px;"></i>' +
          '<strong>Open Food Facts:</strong> ' + data.nombre_sugerido +
          (data.marca_sugerida ? ' &middot; <em>' + data.marca_sugerida + '</em>' : '') +
        '</div>';
    }
    setStatus('', '');
    resultadoEl.innerHTML =
      '<div style="background:var(--bg-card);border:1px solid rgba(232,168,56,0.25);border-radius:var(--r-md);padding:20px;margin-top:12px;">' +
        '<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">' +
          '<div style="width:46px;height:46px;background:var(--c-gold-l);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.3rem;color:var(--c-gold);flex-shrink:0;">' +
            '<i class="fa-solid fa-circle-question"></i>' +
          '</div>' +
          '<div>' +
            '<div style="font-weight:700;font-size:1rem;color:var(--tx-primary);">Producto no registrado</div>' +
            '<div style="font-size:.78rem;color:var(--tx-muted);">EAN: ' + data.codigo + '</div>' +
          '</div>' +
        '</div>' +
        infoExtra +
        '<button onclick="window.escaner_abrirFormulario(\'' + data.codigo + '\',\'' +
          (data.nombre_sugerido||'').replace(/'/g,"\\'") + '\',\'' +
          (data.marca_sugerida||'').replace(/'/g,"\\'") + '\')"' +
          ' class="btn btn-warning w-100">' +
          '<i class="fa-solid fa-plus"></i> Registrar este producto' +
        '</button>' +
      '</div>';
  }

  // ── Modo inventario: agregar a pendientes ──
  function agregarAPendientes(data) {
    var existente = pendientes.findIndex(function(p){ return p.id === data.id; });
    if (existente >= 0) {
      pendientes[existente].cantidad++;
    } else {
      pendientes.push({ id: data.id, nombre: data.nombre, stock: data.stock, cantidad: 1, codigo: data.codigo });
    }
    mostrarListaPendientes();
    setStatus('Escaneado: ' + data.nombre + ' (cantidad: ' + (existente >= 0 ? pendientes[existente].cantidad : 1) + ')', 'ok');
  }

  function mostrarListaPendientes() {
    if (!resultadoEl) return;
    if (pendientes.length === 0) {
      resultadoEl.innerHTML =
        '<div style="text-align:center;padding:24px;color:var(--tx-muted);font-size:.875rem;margin-top:10px;">' +
          '<i class="fa-solid fa-barcode" style="font-size:2rem;display:block;margin-bottom:8px;opacity:.3;"></i>' +
          'Escanea productos para agregar al inventario' +
        '</div>';
      return;
    }
    var filas = pendientes.map(function(p, i) {
      return '<div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--bd-subtle);">' +
        '<div style="flex:1;">' +
          '<div style="font-weight:600;font-size:.88rem;color:var(--tx-primary);">' + p.nombre + '</div>' +
          '<div style="font-size:.74rem;color:var(--tx-muted);">Stock actual: ' + p.stock + '</div>' +
        '</div>' +
        '<div style="display:flex;align-items:center;gap:6px;">' +
          '<button onclick="escaner_ajustarPendiente(' + i + ',-1)" class="btn btn-secondary btn-sm btn-icon-sq">-</button>' +
          '<span style="font-family:var(--font-mono);font-weight:700;font-size:1rem;padding:0 6px;color:var(--c-success);">+' + p.cantidad + '</span>' +
          '<button onclick="escaner_ajustarPendiente(' + i + ',1)" class="btn btn-secondary btn-sm btn-icon-sq">+</button>' +
          '<button onclick="escaner_quitarPendiente(' + i + ')" class="btn btn-danger btn-sm btn-icon-sq"><i class="fa-solid fa-trash"></i></button>' +
        '</div>' +
      '</div>';
    }).join('');

    resultadoEl.innerHTML =
      '<div style="background:var(--bg-card);border:1px solid var(--bd-default);border-radius:var(--r-md);padding:16px;margin-top:12px;">' +
        '<div style="font-family:var(--font-display);font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--tx-secondary);margin-bottom:4px;">' +
          '<i class="fa-solid fa-boxes-stacked me-1"></i> Ajustes pendientes (' + pendientes.length + ' productos)' +
        '</div>' +
        filas +
        '<button onclick="window.escaner_confirmarInventario()" class="btn btn-success w-100 mt-3">' +
          '<i class="fa-solid fa-check"></i> Confirmar todos los ajustes' +
        '</button>' +
      '</div>';
  }

  window.escaner_ajustarPendiente = function(i, delta) {
    pendientes[i].cantidad = Math.max(1, pendientes[i].cantidad + delta);
    mostrarListaPendientes();
  };

  window.escaner_quitarPendiente = function(i) {
    pendientes.splice(i, 1);
    mostrarListaPendientes();
  };

  window.escaner_confirmarInventario = function() {
    if (pendientes.length === 0) return;
    var csrf = (document.cookie.split(';').find(function(c){ return c.trim().startsWith('csrftoken='); })||'').split('=')[1]||'';
    var promesas = pendientes.map(function(p) {
      return fetch('/productos/actualizar-stock-nuevo/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
        body: JSON.stringify({ id: p.id, cantidad: p.cantidad })
      }).then(function(r){ return r.json(); });
    });

    Promise.all(promesas).then(function(resultados) {
      var ok    = resultados.filter(function(r){ return r.ok; }).length;
      var error = resultados.length - ok;
      sesionActualizados += ok;
      actualizarContadorBtn();
      pendientes = [];
      Swal.fire({
        icon: 'success',
        title: 'Inventario actualizado',
        html: '<strong>' + ok + ' producto' + (ok !== 1 ? 's' : '') + '</strong> actualizados correctamente.' +
              (error > 0 ? '<br><small style="color:#e74c3c;">' + error + ' con error</small>' : ''),
        background: '#0e1420', color: '#f0f4ff', confirmButtonColor: '#27ae60', timer: 3500, timerProgressBar: true,
      }).then(function() {
        if (modalBS) modalBS.hide();
        window.location.reload();
      });
    }).catch(function() {
      Swal.fire({ icon:'error', title:'Error de conexion', background:'#0e1420', color:'#f0f4ff', confirmButtonColor:'#c0392b' });
    });
  };

  // ── Historial ──
  function agregarHistorial(nombre, codigo, tipo) {
    historial.unshift({ nombre: nombre, codigo: codigo, tipo: tipo, hora: new Date().toLocaleTimeString('es-CO', {hour:'2-digit',minute:'2-digit',second:'2-digit'}) });
    if (historial.length > 10) historial.pop();
    if (tipo === 'encontrado') sesionActualizados++;
    else sesionNuevos++;
  }

  function renderHistorial() {
    if (!historialEl || historial.length === 0) return;
    historialEl.innerHTML = historial.map(function(h) {
      var color = h.tipo === 'encontrado' ? 'var(--c-success)' : 'var(--c-gold)';
      var icono = h.tipo === 'encontrado' ? 'fa-check' : 'fa-plus';
      return '<div style="display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid var(--bd-subtle);">' +
        '<i class="fa-solid ' + icono + '" style="color:' + color + ';font-size:.7rem;flex-shrink:0;"></i>' +
        '<div style="flex:1;min-width:0;">' +
          '<div style="font-size:.78rem;font-weight:600;color:var(--tx-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + h.nombre + '</div>' +
          '<div style="font-size:.68rem;color:var(--tx-muted);font-family:monospace;">' + h.codigo + '</div>' +
        '</div>' +
        '<span style="font-size:.68rem;color:var(--tx-muted);flex-shrink:0;">' + h.hora + '</span>' +
      '</div>';
    }).join('');
  }

  // ── Contador en el botón ──
  function actualizarContadorBtn() {
    var btn = document.getElementById('btnAbrirEscaner');
    if (!btn) return;
    var total = sesionActualizados + sesionNuevos;
    if (total > 0) {
      btn.innerHTML = '<i class="fa-solid fa-barcode"></i> Escanear <span style="background:rgba(255,255,255,0.25);padding:1px 7px;border-radius:10px;font-size:.78rem;">' + total + '</span>';
    } else {
      btn.innerHTML = '<i class="fa-solid fa-barcode"></i> Escanear';
    }
    if (contadorEl) {
      contadorEl.textContent = total > 0
        ? 'Sesion: ' + sesionActualizados + ' actualizados, ' + sesionNuevos + ' nuevos'
        : '';
    }
  }

  // ── Control de cantidad ──
  window.escaner_cambiarCantidad = function(delta) {
    var el = document.getElementById('escaner-cantidad');
    if (!el) return;
    el.value = Math.max(1, parseInt(el.value || 1) + delta);
  };

  // ── Actualizar stock ──
  window.escaner_agregarStock = function(productoId) {
    var el  = document.getElementById('escaner-cantidad');
    var qty = parseInt(el ? el.value : 1);
    if (!qty || qty < 1) { Swal.fire({ icon:'warning', title:'Cantidad invalida', background:'#0e1420', color:'#f0f4ff', confirmButtonColor:'#c0392b' }); return; }
    var csrf = (document.cookie.split(';').find(function(c){ return c.trim().startsWith('csrftoken='); })||'').split('=')[1]||'';
    fetch('/productos/actualizar-stock-nuevo/', {
      method:'POST', headers:{ 'Content-Type':'application/json','X-CSRFToken':csrf },
      body: JSON.stringify({ id: productoId, cantidad: qty })
    })
    .then(function(r){ return r.json(); })
    .then(function(d) {
      if (d.ok) {
        sesionActualizados++;
        actualizarContadorBtn();
        Swal.fire({
          icon:'success', title:'Stock actualizado',
          html:'<strong>' + d.nombre + '</strong><br>Nuevo stock: <strong style="color:#27ae60;">' + d.stock_nuevo + '</strong>',
          background:'#0e1420', color:'#f0f4ff', confirmButtonColor:'#27ae60', timer:2500, timerProgressBar:true,
        }).then(function(){ if(modalBS) modalBS.hide(); window.location.reload(); });
      } else {
        Swal.fire({ icon:'error', title:'Error', text:d.error, background:'#0e1420', color:'#f0f4ff', confirmButtonColor:'#c0392b' });
      }
    })
    .catch(function(){ Swal.fire({ icon:'error', title:'Error de conexion', background:'#0e1420', color:'#f0f4ff' }); });
  };

  // ── Abrir formulario de creación ──
  window.escaner_abrirFormulario = function (codigo, nombre, marca) {
    // Guardar codigo en sessionStorage para sobrevivir el reset del form
    sessionStorage.setItem('escaner_codigo_pendiente', codigo);
    if (modalBS) modalBS.hide();
    setTimeout(function () {
      var inputCodigo = document.getElementById('add_codigo_barras');
      var inputNombre = document.querySelector('#modalAgregar [name="nombre"]');
      if (inputCodigo) inputCodigo.value = codigo;
      if (inputNombre && nombre) { inputNombre.value = nombre; inputNombre.dispatchEvent(new Event('input')); }
      bootstrap.Modal.getOrCreateInstance(document.getElementById('modalAgregar')).show();
    }, 450);
  };

  // Restaurar codigo del escaner si el modal de agregar se abre
  document.addEventListener('shown.bs.modal', function(e) {
    if (e.target.id !== 'modalAgregar') return;
    var codigoPendiente = sessionStorage.getItem('escaner_codigo_pendiente');
    if (codigoPendiente) {
      var inputCodigo = document.getElementById('add_codigo_barras');
      if (inputCodigo) inputCodigo.value = codigoPendiente;
    }
  });

  // Limpiar cuando se hace submit exitoso
  document.addEventListener('submit', function(e) {
    if (e.target.id === 'formAgregarProducto') {
      sessionStorage.removeItem('escaner_codigo_pendiente');
    }
  });

  // ── Agregar a carrito de venta desde escáner ──
  window.escaner_agregarVenta = function (id, btn) {
    var nombre = btn ? btn.dataset.nombre : '';
    var precio = btn ? parseFloat(btn.dataset.precio) : 0;
    var stock  = btn ? parseInt(btn.dataset.stock)   : 0;
    if (typeof window.carritoVentaAgregar === 'function') {
      window.carritoVentaAgregar(id, nombre, precio, stock);
      beep('ok');
      setStatus('✓ ' + nombre + ' agregado a la venta', 'ok');
    } else {
      setStatus('Abre el modal de Nueva Venta primero.', 'error');
    }
  };

  // ── Helpers ──
  function setStatus(msg, tipo) {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.style.color = tipo === 'error' ? 'var(--c-danger)' :
                           tipo === 'ok'    ? 'var(--c-success)' :
                           tipo === 'info'  ? 'var(--tx-secondary)' : '';
  }

  function resetUI() {
    setStatus('',''); resetResultado();
    areaLector.innerHTML =
      '<div style="text-align:center;color:var(--tx-muted);padding:32px;">' +
        '<i class="fa-solid fa-barcode" style="font-size:3rem;display:block;margin-bottom:12px;opacity:.3;"></i>' +
        '<p style="font-size:.875rem;">Selecciona un modo para escanear</p>' +
      '</div>';
    if (historialEl) historialEl.innerHTML = '';
  }

  function resetResultado() { if (resultadoEl) resultadoEl.innerHTML = ''; }

})();