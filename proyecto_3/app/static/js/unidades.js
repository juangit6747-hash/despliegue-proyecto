var unidadesExistentes = [];

var ABREVIATURAS_VALIDAS = ['kg','g','mg','t','lb','oz','l','ml','kl','cl','m','cm','mm','un','doc','paq','caj','bol','bot','lta','por'];

document.addEventListener('DOMContentLoaded', function () {
    // Recolectar unidades ya registradas
    document.querySelectorAll('tbody .fw-semibold').forEach(function (el) {
        unidadesExistentes.push(el.textContent.trim().toLowerCase());
    });

    // Aplicar validación a todos los formularios de la página
    document.querySelectorAll('form').forEach(function (form) {
        if (form.querySelector('input[name="nombre_unidad"]')) {
            form.addEventListener('submit', function (e) {
                var inputNombre = form.querySelector('input[name="nombre_unidad"]');
                var selectAbrev = form.querySelector('select[name="abreviatura"]');
                var fieldAbrev  = form.querySelector('[name="abreviatura"]');
                var nombre = inputNombre.value.trim();
                var abrev  = selectAbrev ? selectAbrev.value.trim().toLowerCase() : '';
                var abrev  = fieldAbrev ? fieldAbrev.value.trim().toLowerCase() : '';

                if (nombre.length < 2) {
                    e.preventDefault();
                    mostrarErrorUnidad('⚠ El nombre debe tener al menos 2 caracteres.');
                    inputNombre.focus();
                    return;
                }
                if (!abrev || !ABREVIATURAS_VALIDAS.includes(abrev)) {
                    e.preventDefault();
                    mostrarErrorAbreviatura('⚠ Selección de abreviatura obligatoria.');
                    if (selectAbrev) selectAbrev.focus();
                    if (fieldAbrev) fieldAbrev.focus();
                    return;
                }
                // Solo validar duplicados al CREAR (si el formulario no tiene ID de edición)
                if (!form.action.includes('editar') && unidadesExistentes.includes(nombre.toLowerCase())) {
                    e.preventDefault();
                    mostrarErrorUnidad('⚠ Ya existe una unidad con ese nombre.');
                    inputNombre.focus();
                }
            });
        }
    });
});

function bloquearNombreUnidad(input) {
    var antes = input.value;
    var limpio = antes.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ \.]/g, '');
    var limpio = antes.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ .]/g, '');
    limpio = limpio.replace(/ {2,}/g, ' ');
    if (antes !== limpio) {
        input.value = limpio;
        mostrarErrorUnidad('⚠ Solo se permiten letras, números, puntos y espacios.');
        mostrarErrorUnidad('⚠ Solo letras, números y espacios.');
    }
}

function mostrarErrorUnidad(msg) {
    var el = document.getElementById('unidad_error');
    if (el) {
        el.textContent = msg;
        el.style.display = 'block';
        clearTimeout(el._timer);
        el._timer = setTimeout(function () { el.style.display = 'none'; }, 3000);
    }
}

function mostrarErrorAbreviatura(msg) {
    var el = document.getElementById('abreviatura_error');
    if (el) {
        el.textContent = msg;
        el.style.display = 'block';
        clearTimeout(el._timer);
        el._timer = setTimeout(function () { el.style.display = 'none'; }, 3000);
    }
}

function confirmarEliminar(nombre, form) {
    Swal.fire({
        title: '¿Eliminar unidad?',
        html: 'Estás a punto de eliminar <strong>"' + nombre + '"</strong>.<br>Esta acción no se puede deshacer.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then(function (result) {
        if (result.isConfirmed) { form.submit(); }
    });
}