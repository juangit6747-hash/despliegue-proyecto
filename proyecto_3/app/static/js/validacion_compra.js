// Función para mostrar el mensaje de error debajo del campo
function mostrarError(campo, mensaje) {
    var span = document.createElement("span");
    span.className = "error-msg";
    span.style.color = "red";
    span.style.fontSize = "12px";
    span.style.display = "block";
    span.style.marginTop = "4px";
    span.textContent = mensaje;
    campo.parentNode.appendChild(span);
    campo.style.borderColor = "red";
}

// Bloquear escritura de números en el campo nombre
document.addEventListener("DOMContentLoaded", function() {

    var camposNombre = document.querySelectorAll("input[name='nombre']");
    for (var i = 0; i < camposNombre.length; i++) {
        camposNombre[i].addEventListener("keypress", function(e) {
            var char = String.fromCharCode(e.which);
            var regexSoloLetras = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
            if (!regexSoloLetras.test(char)) {
                e.preventDefault();
            }
        });
    }

    // Bloquear caracteres especiales en documento
    var camposDocumento = document.querySelectorAll("input[name='documento']");
    for (var i = 0; i < camposDocumento.length; i++) {
        camposDocumento[i].addEventListener("keypress", function(e) {
            var char = String.fromCharCode(e.which);
            if (!/[0-9]/.test(char)) {
                e.preventDefault();
            }
        });
    }

    // Bloquear caracteres especiales en teléfono y que inicie en 3
    var camposTelefono = document.querySelectorAll("input[name='telefono']");
    for (var i = 0; i < camposTelefono.length; i++) {
        camposTelefono[i].addEventListener("keypress", function(e) {
            var char = String.fromCharCode(e.which);
            if (!/[0-9]/.test(char)) {
                e.preventDefault();
            }
            if (this.value.length === 0 && char !== "3") {
                e.preventDefault();
            }
        });
    }

    // =====================
    // VALIDAR FORMULARIO AGREGAR
    // =====================
    var formAgregar = document.querySelector("#modalAgregarCliente form");

    if (formAgregar) {
        formAgregar.addEventListener("submit", function(e) {

            var valido = true;

            // Limpiar errores previos
            var errores = formAgregar.querySelectorAll(".error-msg");
            for (var i = 0; i < errores.length; i++) errores[i].remove();

            var regexSoloLetras  = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
            var regexSoloNumeros = /^[0-9]+$/;
            var regexEmail       = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;

            // Validar Nombre
            var nombre = formAgregar.querySelector("input[name='nombre']");
            if (nombre.value.trim() === "") {
                mostrarError(nombre, "El nombre es obligatorio.");
                valido = false;
            } else if (!regexSoloLetras.test(nombre.value.trim())) {
                mostrarError(nombre, "El nombre no puede contener números ni caracteres especiales.");
                valido = false;
            } else if (nombreDuplicado(nombre.value.trim(), null)) {
                mostrarError(nombre, "Ya existe un cliente con ese nombre.");
                valido = false;
            }

            // Validar Documento: entre 6 y 12 dígitos ✅
            var documento = formAgregar.querySelector("input[name='documento']");
            if (documento.value.trim() === "") {
                mostrarError(documento, "El documento es obligatorio.");
                valido = false;
            } else if (!regexSoloNumeros.test(documento.value.trim())) {
                mostrarError(documento, "El documento solo puede contener números.");
                valido = false;
            } else if (documento.value.trim().length < 6 || documento.value.trim().length > 12) {
                mostrarError(documento, "El documento debe tener entre 6 y 12 dígitos.");
                valido = false;
            } else if (documentoDuplicado(documento.value.trim(), null)) {
                mostrarError(documento, "Ya existe un cliente con ese documento.");
                valido = false;
            }

            // Validar Teléfono: entre 7 y 15 dígitos ✅
            var telefono = formAgregar.querySelector("input[name='telefono']");
            if (telefono.value.trim() === "") {
                mostrarError(telefono, "El teléfono es obligatorio.");
                valido = false;
            } else if (!regexSoloNumeros.test(telefono.value.trim())) {
                mostrarError(telefono, "El teléfono solo puede contener números.");
                valido = false;
            } else if (telefono.value.trim().length < 7 || telefono.value.trim().length > 10) {
                mostrarError(telefono, "El teléfono debe tener entre 7 y 10 dígitos.");
                valido = false;
            } else if (telefono.value.trim()[0] !== "3") {
                mostrarError(telefono, "El teléfono debe iniciar con 3.");
                valido = false;
            } else if (telefonoDuplicado(telefono.value.trim(), null)) {
                mostrarError(telefono, "Ya existe un cliente con ese teléfono.");
                valido = false;
            }

            // Validar Email ✅
            var email = formAgregar.querySelector("input[name='email']");
            if (email.value.trim() === "") {
                mostrarError(email, "El email es obligatorio.");
                valido = false;
            } else if (!regexEmail.test(email.value.trim())) {
                mostrarError(email, "Ingrese un email válido (ejemplo: cliente@empresa.com).");
                valido = false;
            } else if (emailDuplicado(email.value.trim(), null)) {
                mostrarError(email, "Ya existe un cliente con ese email.");
                valido = false;
            }

            // Validar Dirección: mínimo 5 caracteres ✅
            var direccion = formAgregar.querySelector("input[name='direccion']");
            if (direccion.value.trim() === "") {
                mostrarError(direccion, "La dirección es obligatoria.");
                valido = false;
            } else if (direccion.value.trim().length < 5) {
                mostrarError(direccion, "La dirección debe tener mínimo 5 caracteres.");
                valido = false;
            }

            // Validar Estado
            var estado = formAgregar.querySelector("select[name='estado']");
            if (estado.value === "") {
                mostrarError(estado, "Seleccione un estado.");
                valido = false;
            }

            if (!valido) e.preventDefault();
        });
    }

    // =====================
    // VALIDAR FORMULARIOS EDITAR
    // =====================
    var formsEditar = document.querySelectorAll("[id^='modalEditarCliente'] form");

    for (var j = 0; j < formsEditar.length; j++) {
        formsEditar[j].addEventListener("submit", function(e) {

            var formActual = e.target;
            var valido = true;

            // Limpiar errores previos
            var errores = formActual.querySelectorAll(".error-msg");
            for (var i = 0; i < errores.length; i++) errores[i].remove();

            // Obtener id actual desde la action
            var action = formActual.getAttribute("action");
            var partes = action.split("/");
            var idActual = null;
            for (var k = 0; k < partes.length; k++) {
                if (partes[k] !== "" && !isNaN(partes[k])) {
                    idActual = partes[k];
                }
            }

            var regexSoloLetras  = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
            var regexSoloNumeros = /^[0-9]+$/;
            var regexEmail       = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;

            // Validar Nombre
            var nombre = formActual.querySelector("input[name='nombre']");
            if (nombre.value.trim() === "") {
                mostrarError(nombre, "El nombre es obligatorio.");
                valido = false;
            } else if (!regexSoloLetras.test(nombre.value.trim())) {
                mostrarError(nombre, "El nombre no puede contener números ni caracteres especiales.");
                valido = false;
            } else if (nombreDuplicado(nombre.value.trim(), idActual)) {
                mostrarError(nombre, "Ya existe un cliente con ese nombre.");
                valido = false;
            }

            // Validar Documento: entre 6 y 12 dígitos ✅
            var documento = formActual.querySelector("input[name='documento']");
            if (documento.value.trim() === "") {
                mostrarError(documento, "El documento es obligatorio.");
                valido = false;
            } else if (!regexSoloNumeros.test(documento.value.trim())) {
                mostrarError(documento, "El documento solo puede contener números.");
                valido = false;
            } else if (documento.value.trim().length < 6 || documento.value.trim().length > 12) {
                mostrarError(documento, "El documento debe tener entre 6 y 12 dígitos.");
                valido = false;
            } else if (documentoDuplicado(documento.value.trim(), idActual)) {
                mostrarError(documento, "Ya existe un cliente con ese documento.");
                valido = false;
            }

            // Validar Teléfono: entre 7 y 15 dígitos ✅
            var telefono = formActual.querySelector("input[name='telefono']");
            if (telefono.value.trim() === "") {
                mostrarError(telefono, "El teléfono es obligatorio.");
                valido = false;
            } else if (!regexSoloNumeros.test(telefono.value.trim())) {
                mostrarError(telefono, "El teléfono solo puede contener números.");
                valido = false;
            } else if (telefono.value.trim().length < 7 || telefono.value.trim().length > 15) {
                mostrarError(telefono, "El teléfono debe tener entre 7 y 15 dígitos.");
                valido = false;
            } else if (telefono.value.trim()[0] !== "3") {
                mostrarError(telefono, "El teléfono debe iniciar con 3.");
                valido = false;
            } else if (telefonoDuplicado(telefono.value.trim(), idActual)) {
                mostrarError(telefono, "Ya existe un cliente con ese teléfono.");
                valido = false;
            }

            // Validar Email ✅
            var email = formActual.querySelector("input[name='email']");
            if (email.value.trim() === "") {
                mostrarError(email, "El email es obligatorio.");
                valido = false;
            } else if (!regexEmail.test(email.value.trim())) {
                mostrarError(email, "Ingrese un email válido (ejemplo: cliente@empresa.com).");
                valido = false;
            } else if (emailDuplicado(email.value.trim(), idActual)) {
                mostrarError(email, "Ya existe un cliente con ese email.");
                valido = false;
            }

            // Validar Dirección: mínimo 5 caracteres ✅
            var direccion = formActual.querySelector("input[name='direccion']");
            if (direccion.value.trim() === "") {
                mostrarError(direccion, "La dirección es obligatoria.");
                valido = false;
            } else if (direccion.value.trim().length < 5) {
                mostrarError(direccion, "La dirección debe tener mínimo 5 caracteres.");
                valido = false;
            }

            // Validar Estado
            var estado = formActual.querySelector("select[name='estado']");
            if (estado.value === "") {
                mostrarError(estado, "Seleccione un estado.");
                valido = false;
            }

            if (!valido) e.preventDefault();
        });
    }

});

// =====================
// FUNCIONES PARA DETECTAR DUPLICADOS
// =====================

function nombreDuplicado(valor, idExcluir) {
    var filas = document.querySelectorAll("table tbody tr");
    for (var i = 0; i < filas.length; i++) {
        var celdas = filas[i].querySelectorAll("td");
        if (celdas.length > 0) {
            var idFila      = celdas[0].textContent.trim();
            var nombreFila  = celdas[1].textContent.trim().toLowerCase();
            if (nombreFila === valor.toLowerCase() && idFila !== idExcluir) return true;
        }
    }
    return false;
}

function documentoDuplicado(valor, idExcluir) {
    var filas = document.querySelectorAll("table tbody tr");
    for (var i = 0; i < filas.length; i++) {
        var celdas = filas[i].querySelectorAll("td");
        if (celdas.length > 0) {
            var idFila        = celdas[0].textContent.trim();
            var documentoFila = celdas[2].textContent.trim();
            if (documentoFila === valor && idFila !== idExcluir) return true;
        }
    }
    return false;
}

function telefonoDuplicado(valor, idExcluir) {
    var filas = document.querySelectorAll("table tbody tr");
    for (var i = 0; i < filas.length; i++) {
        var celdas = filas[i].querySelectorAll("td");
        if (celdas.length > 0) {
            var idFila       = celdas[0].textContent.trim();
            var telefonoFila = celdas[3].textContent.trim();
            if (telefonoFila === valor && idFila !== idExcluir) return true;
        }
    }
    return false;
}

function emailDuplicado(valor, idExcluir) {
    var filas = document.querySelectorAll("table tbody tr");
    for (var i = 0; i < filas.length; i++) {
        var celdas = filas[i].querySelectorAll("td");
        if (celdas.length > 0) {
            var idFila    = celdas[0].textContent.trim();
            var emailFila = celdas[4].textContent.trim().toLowerCase();
            if (emailFila === valor.toLowerCase() && idFila !== idExcluir) return true;
        }
    }
    return false;
}