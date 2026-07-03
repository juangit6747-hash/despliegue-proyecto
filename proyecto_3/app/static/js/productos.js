// ── Validaciones de campos ────────────────────────────────────────

function bloquearNumeros(input, errorId) {
    var antes = input.value;
    var limpio = input.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s\-\.%&\/]/g, '');
    limpio = limpio.replace(/ {2,}/g, ' ');
    if (antes !== limpio) {
        input.value = limpio;
        mostrarError(errorId, 'El nombre solo permite letras. No se aceptan números.');
    } else {
        ocultarError(errorId);
    }
}

function validarPrecio(input, errorId) {
    var limpio = input.value.replace(/[^\d]/g, '');
    limpio = limpio.replace(/^0+(\d)/, '$1');
    if (limpio && parseInt(limpio) > 800000) {
        limpio = '800000';
        mostrarError(errorId, 'El precio máximo es $800.000.');
    } else {
        ocultarError(errorId);
    }
    input.value = limpio;
}

function validarStock(input, errorId) {
    var limpio = input.value.replace(/[^\d]/g, '');
    if (limpio.length > 1) limpio = limpio.replace(/^0+/, '');
    if (parseInt(limpio) > 1000) {
        limpio = '1000';
        mostrarError(errorId, '⚠ Has llegado al límite máximo de stock (1000 unidades).');
    } else if (input.value !== limpio) {
        mostrarError(errorId, '⚠ El stock solo acepta números enteros.');
    }
    input.value = limpio;
}

function mostrarError(errorId, msg) {
    var el = document.getElementById(errorId);
    if (el) {
        el.textContent = '⚠ ' + msg;
        el.style.display = 'block';
        clearTimeout(el._timer);
        el._timer = setTimeout(function () {
            el.style.display = 'none';
        }, 3000);
    }
}

function ocultarError(errorId) {
    var el = document.getElementById(errorId);
    if (el) el.style.display = 'none';
}

// ── Ver producto con SweetAlert ───────────────────────────────────

function verProducto(id, nombre, precio, stock, marca, tipo, unidad) {
    Swal.fire({
        title: nombre,
        icon: 'info',
        html:
            '<table class="table text-start mb-0">' +
            '<tr><th>ID</th><td>' + id + '</td></tr>' +
            '<tr><th>Nombre</th><td>' + nombre + '</td></tr>' +
            '<tr><th>Precio</th><td>$' + precio + '</td></tr>' +
            '<tr><th>Stock</th><td>' + stock + ' unidades</td></tr>' +
            '<tr><th>Marca</th><td>' + marca + '</td></tr>' +
            '<tr><th>Tipo</th><td>' + tipo + '</td></tr>' +
            '<tr><th>Unidad</th><td>' + unidad + '</td></tr>' +
            '</table>',
        confirmButtonText: 'Cerrar',
        showCancelButton: false,
        width: '420px',
    });
}

// ── Eliminar producto con SweetAlert ─────────────────────────────

function eliminarProducto(url, nombre) {
    Swal.fire({
        title: '¿Eliminar producto?',
        html: 'Estás a punto de eliminar <strong>"' + nombre + '"</strong>.<br>Esta acción no se puede deshacer.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: null,
        cancelButtonColor: null,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then(function (result) {
        if (result.isConfirmed) {
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = url;
            var csrf = document.createElement('input');
            csrf.type = 'hidden';
            csrf.name = 'csrfmiddlewaretoken';
            csrf.value = document.cookie.split('; ')
                .find(row => row.startsWith('csrftoken='))
                .split('=')[1];
            form.appendChild(csrf);
            document.body.appendChild(form);
            form.submit();
        }
    });
}

// ── Borrador en sessionStorage ────────────────────────────────────

var SK = 'prod_modal_draft';

function guardarBorrador() {
    var draft = {
        nombre:   $('[name="nombre"]', '#formAgregarProducto').val(),
        precio:   $('[name="precio"]', '#formAgregarProducto').val(),
        stock:    $('[name="stock"]',  '#formAgregarProducto').val(),
        idMarca:  $('#add_idMarca').val(),
        idTipo:   $('#add_idTipo').val(),
        idUnidad: $('#add_idUnidad').val(),
    };
    sessionStorage.setItem(SK, JSON.stringify(draft));
}

function restaurarBorrador() {
    var raw = sessionStorage.getItem(SK);
    if (!raw) return;
    try {
        var d = JSON.parse(raw);
        $('[name="nombre"]', '#formAgregarProducto').val(d.nombre || '');
        $('[name="precio"]', '#formAgregarProducto').val(d.precio || '');
        $('[name="stock"]',  '#formAgregarProducto').val(d.stock  || '');
        if (d.idMarca)  { $('#add_idMarca').val(d.idMarca).trigger('change'); }
        if (d.idTipo)   { $('#add_idTipo').val(d.idTipo).trigger('change');   }
        if (d.idUnidad) { $('#add_idUnidad').val(d.idUnidad).trigger('change'); }
    } catch (e) {}
}

function limpiarBorrador() {
    sessionStorage.removeItem(SK);
}

// ── Lógica principal ──────────────────────────────────────────────

$(document).ready(function () {

    // Leer variable Django pasada desde el HTML via data-attribute
    var config         = document.getElementById('productos-config');
    var abrirModal     = config && config.dataset.abrirModal === 'true';
    var params         = new URLSearchParams(window.location.search);
    var vieneGestionar = params.get('abrir_modal') === '1';

    // Si no viene de Gestionar ni hay error Django: limpiar borrador residual
    if (!vieneGestionar && !abrirModal) {
        limpiarBorrador();
    }

    var s2opts = {
        theme: 'bootstrap-5',
        width: '100%',
        language: {
            noResults: function () { return 'No se encontraron resultados'; },
            searching: function () { return 'Buscando...'; },
        },
    };

    // ── Select2 modal Agregar ─────────────────────────────────────
    function initSelect2Agregar() {
        $('#add_idMarca, #add_idTipo, #add_idUnidad').each(function () {
            if (!$(this).hasClass('select2-hidden-accessible')) {
                $(this).select2($.extend({}, s2opts, {
                    dropdownParent: $('#modalAgregar'),
                    placeholder: $(this).find('option:first').text(),
                }));
            }
        });
    }

    $('#modalAgregar').on('shown.bs.modal', function () {
        initSelect2Agregar();
        restaurarBorrador();
    });

    // Guardar borrador solo al hacer clic en "Gestionar..." dentro del modal
    $('#modalAgregar').on('click', 'a[href*="next=productos"]', function () {
        guardarBorrador();
    });

    // Limpiar borrador al enviar el form con éxito
    $('#formAgregarProducto').on('submit', function () {
        limpiarBorrador();
    });

    $('#modalAgregar').on('hide.bs.modal', function () {
        // Destruir Select2 antes de cerrar para evitar conflicto con backdrop
        $('#add_idMarca, #add_idTipo, #add_idUnidad').each(function () {
            if ($(this).hasClass('select2-hidden-accessible')) {
                $(this).select2('destroy');
            }
        });
    });

    $('#modalAgregar').on('hidden.bs.modal', function () {
        // Limpiar borrador y form al cerrar
        limpiarBorrador();
        $('#formAgregarProducto')[0].reset();
    });

    // ── Select2 modales Editar ────────────────────────────────────
    $('[id^="modalEditar"]').each(function () {
        var $modal = $(this);
        var pid    = $modal.attr('id').replace('modalEditar', '');

        $modal.on('shown.bs.modal', function () {
            $modal.find('.select2-editar-' + pid).each(function () {
                if (!$(this).hasClass('select2-hidden-accessible')) {
                    $(this).select2($.extend({}, s2opts, {
                        dropdownParent: $modal,
                        placeholder: $(this).find('option:first').text(),
                    }));
                }
            });
        });
    });

    // ── Auto-abrir modal (error Django o vuelta de Gestionar) ─────
    if (abrirModal || vieneGestionar) {
        bootstrap.Modal.getOrCreateInstance(document.getElementById('modalAgregar')).show();
    }

});