"""Vistas para gestión de clientes"""
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from app.decorators import admin_login_required
from app.services.notifications import (
    notificacion_cliente_creado,
    notificacion_cliente_inactivo,
)
from ...models import Cliente

PATRON_EMAIL = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)*\.[a-zA-Z]{2,}$'


def _validar_cliente(nombre, documento, telefono, email, direccion, estado, cliente_id=None):
    errores = []
    if not nombre or len(nombre) < 3:
        errores.append('El nombre debe tener al menos 3 caracteres.')
    elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', nombre):
        errores.append('El nombre solo puede contener letras y espacios.')
    if not documento:
        errores.append('El documento es obligatorio.')
    elif not documento.isdigit():
        errores.append('El documento solo puede contener números.')
    elif len(documento) < 6 or len(documento) > 12:
        errores.append('El documento debe tener entre 6 y 12 dígitos.')
    else:
        qs = Cliente.objects.filter(documento=documento)
        if cliente_id:
            qs = qs.exclude(id=cliente_id)
        if qs.exists():
            errores.append('Ya existe un cliente con ese documento.')
    if not telefono:
        errores.append('El teléfono es obligatorio.')
    elif not telefono.isdigit():
        errores.append('El teléfono solo puede contener números.')
    elif len(telefono) < 7 or len(telefono) > 15:
        errores.append('El teléfono debe tener entre 7 y 15 dígitos.')
    if not email:
        errores.append('El email es obligatorio.')
    elif not re.match(PATRON_EMAIL, email):
        errores.append('El email no tiene un formato válido.')
    elif '.' not in email.split('@')[-1] or len(email.split('@')[-1].split('.')[-1]) < 2:
        errores.append('El dominio del email no es válido.')
    elif len(email.split('@')[0]) < 2:
        errores.append('La dirección de email es demasiado corta.')
    else:
        qs = Cliente.objects.filter(email=email)
        if cliente_id:
            qs = qs.exclude(id=cliente_id)
        if qs.exists():
            errores.append('Ya existe un cliente con ese email.')
    if not direccion or len(direccion) < 5:
        errores.append('La dirección debe tener al menos 5 caracteres.')
    if estado not in ['activo', 'inactivo']:
        errores.append('Debe seleccionar un estado válido.')
    return errores


@method_decorator(admin_login_required, name='dispatch')
class ClientesView(View):
    def get(self, request):
        clientes_list = Cliente.objects.all()
        busqueda = request.GET.get('busqueda', '').strip()
        if busqueda:
            clientes_list = clientes_list.filter(nombre__icontains=busqueda)
        estado = request.GET.get('estado', '').strip()
        if estado:
            clientes_list = clientes_list.filter(estado=estado)
        return render(request, 'Clientes/clientes.html', {'clientes': clientes_list})


@method_decorator(admin_login_required, name='dispatch')
class CrearClienteView(View):
    def post(self, request):
        nombre    = request.POST.get('nombre', '').strip()
        documento = request.POST.get('documento', '').strip()
        telefono  = request.POST.get('telefono', '').strip()
        email     = request.POST.get('email', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        estado    = request.POST.get('estado', '').strip()

        errores = _validar_cliente(nombre, documento, telefono, email, direccion, estado)
        if errores:
            for e in errores:
                messages.error(request, e)
        else:
            try:
                cliente = Cliente.objects.create(
                    nombre=nombre, documento=documento, telefono=telefono,
                    email=email, direccion=direccion, estado=estado,
                )
                notificacion_cliente_creado(cliente, request.user)
                messages.success(request, f'Cliente "{nombre}" creado exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al crear el cliente: {str(e)}')
        return redirect('clientes')


@method_decorator(admin_login_required, name='dispatch')
class EditarClienteView(View):
    def post(self, request, id):
        cliente = get_object_or_404(Cliente, id=id)
        nombre    = request.POST.get('nombre', '').strip()
        documento = request.POST.get('documento', '').strip()
        telefono  = request.POST.get('telefono', '').strip()
        email     = request.POST.get('email', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        estado    = request.POST.get('estado', '').strip()

        errores = _validar_cliente(nombre, documento, telefono, email, direccion, estado, cliente_id=id)
        if errores:
            for e in errores:
                messages.error(request, e)
        else:
            try:
                estado_anterior = cliente.estado
                cliente.nombre = nombre; cliente.documento = documento
                cliente.telefono = telefono; cliente.email = email
                cliente.direccion = direccion; cliente.estado = estado
                cliente.save()
                # Notificar si pasó a inactivo
                if estado_anterior == 'activo' and estado == 'inactivo':
                    notificacion_cliente_inactivo(cliente, request.user)
                messages.success(request, f'Cliente "{cliente.nombre}" actualizado exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al actualizar: {str(e)}')
        return redirect('clientes')


@method_decorator(admin_login_required, name='dispatch')
class EliminarClienteView(View):
    def post(self, request, id):
        cliente = get_object_or_404(Cliente, id=id)
        try:
            nombre = cliente.nombre
            cliente.delete()
            messages.success(request, f'Cliente "{nombre}" eliminado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar: {str(e)}')
        return redirect('clientes')


@method_decorator(admin_login_required, name='dispatch')
class ClientesJsonView(View):
    def get(self, request):
        lista = list(Cliente.objects.all().values(
            'id', 'nombre', 'documento', 'telefono', 'email', 'direccion', 'estado'
        ))
        return JsonResponse({'clientes': lista})


clientes         = ClientesView.as_view()
crear_cliente    = CrearClienteView.as_view()
editar_cliente   = EditarClienteView.as_view()
eliminar_cliente = EliminarClienteView.as_view()
clientes_json    = ClientesJsonView.as_view()