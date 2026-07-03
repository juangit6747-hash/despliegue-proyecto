/**
 * ventas.js — Carrito de ventas
 * Compatible con Ventas.html v2
 */
(function () {
  'use strict';

  /* ── Carrito crear ── */
  var carrito = [];

  function fmt(n) { return '$' + Number(n).toLocaleString('es-CO'); }

  function renderCarrito() {
    var tbody   = document.getElementById('filasCarrito');
    var ocultos = document.getElementById('camposOcultosProductos');
    var totalEl = document.getElementById('totalCarrito');
    var wrap    = document.getElementById('tablaCarritoWrap');
    var vacio   = document.getElementById('msgCarritoVacio');
    var titulo  = document.getElementById('tituloCarrito');
    if (!tbody) return;

    tbody.innerHTML  = '';
    ocultos.innerHTML = '';
    var total = 0;

    carrito.forEach(function (item, idx) {
      var sub = item.precio * item.cantidad;
      total  += sub;
      var tr  = document.createElement('tr');
      tr.innerHTML =
        '<td><span style="font-weight:600;">' + item.nombre + '</span>' +
        '<br><small style="color:var(--tx-muted);">' + fmt(item.precio) + ' c/u</small></td>' +
        '<td><div style="display:flex;align-items:center;gap:4px;">' +
        '<button type="button" class="btn btn-secondary btn-sm btn-icon-sq" onclick="carritoRestar(' + idx + ')">-</button>' +
        '<span style="font-weight:700;padding:0 6px;">' + item.cantidad + '</span>' +
        '<button type="button" class="btn btn-secondary btn-sm btn-icon-sq" onclick="carritoSumar(' + idx + ')">+</button>' +
        '</div></td>' +
        '<td style="text-align:right;font-family:monospace;font-weight:700;color:var(--c-gold);">' + fmt(sub) + '</td>' +
        '<td><button type="button" class="btn btn-danger btn-sm btn-icon-sq" onclick="carritoQuitar(' + idx + ')">' +
        '<i class="fa-solid fa-trash"></i></button></td>';
      tbody.appendChild(tr);

      // Campos ocultos para el POST
      ['producto_id[]', 'producto_nombre[]', 'producto_precio[]', 'producto_cantidad[]']
        .forEach(function (name, ni) {
          var inp = document.createElement('input');
          inp.type  = 'hidden';
          inp.name  = name;
          inp.value = [item.productoId, item.nombre, item.precio, item.cantidad][ni];
          ocultos.appendChild(inp);
        });
    });

    if (totalEl) totalEl.textContent = fmt(total);
    var tieneItems = carrito.length > 0;
    if (wrap)   wrap.classList.toggle('d-none', !tieneItems);
    if (vacio)  vacio.style.display  = tieneItems ? 'none' : 'block';
    if (titulo) titulo.classList.toggle('d-none', !tieneItems);
  }

  window.agregarProducto = function (id, nombre, precio, stock) {
    var dup = carrito.findIndex(function (x) { return x.productoId == id; });
    var alerta = document.getElementById('alertaProductoDuplicado');
    var vacios = document.getElementById('alertaCarritoVacio');
    if (vacios) vacios.classList.add('d-none');

    if (dup >= 0) {
      if (carrito[dup].cantidad < stock) {
        carrito[dup].cantidad++;
      } else {
        if (alerta) { alerta.classList.remove('d-none'); setTimeout(function(){ alerta.classList.add('d-none'); }, 2500); }
        return;
      }
    } else {
      if (alerta) alerta.classList.add('d-none');
      carrito.push({ productoId: id, nombre: nombre, precio: parseFloat(precio), cantidad: 1 });
    }
    renderCarrito();
  };

  window.carritoSumar = function (idx) {
    carrito[idx].cantidad++;
    renderCarrito();
  };

  window.carritoRestar = function (idx) {
    if (carrito[idx].cantidad > 1) { carrito[idx].cantidad--; renderCarrito(); }
  };

  window.carritoQuitar = function (idx) {
    carrito.splice(idx, 1);
    renderCarrito();
  };

  document.addEventListener('DOMContentLoaded', function () {
    var modalCrear = document.getElementById('modalCrearVenta');
    if (!modalCrear) return;

    /* Búsqueda de productos */
    var busqueda = document.getElementById('busquedaProductos');
    if (busqueda) {
      busqueda.addEventListener('input', function () {
        var term = this.value.toLowerCase();
        document.querySelectorAll('.producto-card').forEach(function (c) {
          c.style.display = c.getAttribute('data-nombre').includes(term) ? '' : 'none';
        });
      });
    }

    /* Validación cliente */
    var inputCliente = document.getElementById('inputClienteCrear');
    var feedbackCliente = document.getElementById('feedbackCliente');
    var contadorCliente = document.getElementById('contadorCliente');
    if (inputCliente) {
      inputCliente.addEventListener('input', function () {
        var val = this.value.trim();
        if (contadorCliente) contadorCliente.textContent = val.length + '/30 caracteres';
        if (!feedbackCliente) return;
        if (val.length === 0) {
          feedbackCliente.textContent = '⚠ Nombre obligatorio.';
          feedbackCliente.style.color = '#dc3545';
        } else if (val.length < 3) {
          feedbackCliente.textContent = '⚠ Mínimo 3 caracteres.';
          feedbackCliente.style.color = '#fd7e14';
        } else {
          feedbackCliente.textContent = '✓ OK';
          feedbackCliente.style.color = '#198754';
        }
      });
    }

    /* Validación submit */
    var form = document.getElementById('formCrearVenta');
    if (form) {
      form.addEventListener('submit', function (e) {
        var alertaVacio = document.getElementById('alertaCarritoVacio');
        var alertaEstado = document.getElementById('feedbackEstado');
        var estado = document.getElementById('selectEstado');
        var cliente = document.getElementById('inputClienteCrear');
        var ok = true;

        if (carrito.length === 0) {
          if (alertaVacio) alertaVacio.classList.remove('d-none');
          ok = false;
        }
        if (estado && !estado.value) {
          if (alertaEstado) { alertaEstado.textContent = '⚠ Selecciona un estado.'; alertaEstado.style.color = '#dc3545'; }
          ok = false;
        }
        if (cliente && cliente.value.trim().length < 3) {
          var fb = document.getElementById('feedbackCliente');
          if (fb) { fb.textContent = '⚠ Nombre obligatorio (mín. 3 caracteres).'; fb.style.color = '#dc3545'; }
          ok = false;
        }
        if (!ok) e.preventDefault();
      });
    }

    /* Reset al cerrar */
    modalCrear.addEventListener('hidden.bs.modal', function () {
      carrito.length = 0;
      renderCarrito();
      var ids = ['inputClienteCrear','feedbackCliente','busquedaProductos'];
      ids.forEach(function(id){ var el = document.getElementById(id); if(el) el.value = ''; });
      var cc = document.getElementById('contadorCliente'); if(cc) cc.textContent = '0/30 caracteres';
      var se = document.getElementById('selectEstado');    if(se) se.value = '';
      var fe = document.getElementById('feedbackEstado');  if(fe) fe.textContent = '';
      document.querySelectorAll('.producto-card').forEach(function(c){ c.style.display = ''; });
    });
  });

  // ── Confirmar completar venta ──
  window.confirmarCompletarVenta = function (id, cliente) {
    Swal.fire({
      icon: 'question',
      title: '¿Confirmar venta?',
      html: '¿Deseas confirmar la venta del cliente <strong>' + cliente + '</strong>?<br><span style="font-size:.85rem;color:var(--tx-muted);">Esta acción marcará la venta como completada.</span>',
      showCancelButton: true,
      confirmButtonText: '<i class="fa-solid fa-check me-1"></i> Sí, confirmar',
      cancelButtonText: 'Cancelar',
      confirmButtonColor: '#27ae60',
      cancelButtonColor: '#555',
      background: '#0e1420',
      color: '#f0f4ff',
    }).then(function(r) {
      if (r.isConfirmed) document.getElementById('formCompletar' + id).submit();
    });
  };

  // ── Exponer para el escáner de ventas ──
  // El escáner llama a esta función cuando lee un producto en modo venta
  window.carritoVentaAgregar = function (id, nombre, precio, stock) {
    // Abrir el modal de crear venta si no está abierto
    var modalCrear = document.getElementById('modalCrearVenta');
    if (modalCrear) {
      var bsModal = bootstrap.Modal.getOrCreateInstance(modalCrear);
      bsModal.show();
    }
    // Agregar al carrito (reutiliza la función ya existente)
    window.agregarProducto(String(id), nombre, parseFloat(precio), stock);
  };

})();
