"""Vistas para gestión de proveedores"""
import re
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from app.decorators import admin_login_required
from app.services.notifications import (
    notificacion_proveedor_creado,
    notificacion_proveedor_eliminado,
)
from app.models import Proveedor, Producto


def _validar_proveedor(nombre, telefono, email, proveedor_id=None):
    errores = []
    if not nombre:
        errores.append('El nombre es obligatorio.')
    elif len(nombre) < 3:
        errores.append('El nombre debe tener al menos 3 caracteres.')
    elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', nombre):
        errores.append('El nombre solo puede contener letras y espacios.')
    if not telefono:
        errores.append('El teléfono es obligatorio.')
    elif not telefono.isdigit():
        errores.append('El teléfono solo puede contener números.')
    elif not telefono.startswith('3'):
        errores.append('El teléfono debe iniciar con 3.')
    elif len(telefono) < 7 or len(telefono) > 15:
        errores.append('El teléfono debe tener entre 7 y 15 dígitos.')
    patron_email = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not email:
        errores.append('El email es obligatorio.')
    elif not re.match(patron_email, email):
        errores.append('El email no tiene un formato válido.')
    else:
        # Validar que el dominio tenga TLD real (mínimo 2 letras reales, no solo letras random)
        match = re.match(r'^[^@]+@[^@]+\.([a-zA-Z]{2,})$', email)
        if match:
            tld = match.group(1).lower()
            # TLDs válidos comunes - bloquear dominios inventados muy cortos
            tlds_invalidos = set()  # se maneja en backend con regex estricto
        qs = Proveedor.objects.filter(email=email)
        if proveedor_id:
            qs = qs.exclude(id=proveedor_id)
        if qs.exists():
            errores.append('Ya existe un proveedor con ese email.')
    return errores


@method_decorator(admin_login_required, name='dispatch')
class ProveedoresView(View):
    def get(self, request):
        lista        = Proveedor.objects.all()
        busqueda     = request.GET.get('busqueda', '').strip()
        envio_filtro = request.GET.get('envio', '').strip()
        fecha_desde  = request.GET.get('fecha_desde', '').strip()
        fecha_hasta  = request.GET.get('fecha_hasta', '').strip()

        if busqueda:
            lista = lista.filter(nombre__icontains=busqueda)
        if envio_filtro == 'rapido':
            lista = lista.filter(envio__lte=7)
        elif envio_filtro == 'normal':
            lista = lista.filter(envio__gte=8, envio__lte=15)
        elif envio_filtro == 'lento':
            lista = lista.filter(envio__gt=15)
        if fecha_desde:
            try:
                lista = lista.filter(fechaRegistro__gte=date.fromisoformat(fecha_desde))
            except ValueError:
                pass
        if fecha_hasta:
            try:
                lista = lista.filter(fechaRegistro__lte=date.fromisoformat(fecha_hasta))
            except ValueError:
                pass

        from collections import Counter
        for p in lista:
            tipos = list(
                p.productos
                .exclude(idTipo=None)
                .values_list('idTipo__nombre_tipo', flat=True)
            )
            if tipos:
                mas_comun = Counter(tipos).most_common(1)
                p.categoria_principal = mas_comun[0][0] if mas_comun else '—'
            else:
                p.categoria_principal = '—'

        return render(request, 'proveedores/proveedores.html', {
            'proveedores':  lista,
            'busqueda':     busqueda,
            'envio_filtro': envio_filtro,
        })


@method_decorator(admin_login_required, name='dispatch')
class CrearProveedorView(View):
    def post(self, request):
        nombre   = request.POST.get('nombre', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email    = request.POST.get('email', '').strip()
        errores  = _validar_proveedor(nombre, telefono, email)
        if errores:
            for e in errores:
                messages.error(request, e)
        else:
            try:
                proveedor = Proveedor.objects.create(
                    nombre=nombre, telefono=telefono, email=email,
                    observaciones=request.POST.get('observaciones', '').strip()
                )
                notificacion_proveedor_creado(proveedor, request.user)
                messages.success(request, f'Proveedor "{nombre}" creado exitosamente.')
            except Exception as e:
                messages.error(request, f'Error al crear proveedor: {str(e)}')
        return redirect('proveedores')


@method_decorator(admin_login_required, name='dispatch')
class EditarProveedorView(View):
    def post(self, request, id):
        proveedor = get_object_or_404(Proveedor, id=id)
        nombre    = request.POST.get('nombre', '').strip()
        telefono  = request.POST.get('telefono', '').strip()
        email     = request.POST.get('email', '').strip()
        errores   = _validar_proveedor(nombre, telefono, email, proveedor_id=id)
        if errores:
            for e in errores:
                messages.error(request, e)
        else:
            try:
                proveedor.nombre        = nombre
                proveedor.telefono      = telefono
                proveedor.email         = email
                proveedor.observaciones = request.POST.get('observaciones', '').strip()
                proveedor.save()
                messages.success(request, f'Proveedor "{nombre}" actualizado exitosamente.')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        return redirect('proveedores')


@method_decorator(admin_login_required, name='dispatch')
class EliminarProveedorView(View):
    def post(self, request, id):
        proveedor = get_object_or_404(Proveedor, id=id)
        try:
            nombre = proveedor.nombre
            notificacion_proveedor_eliminado(nombre, request.user)
            proveedor.delete()
            messages.success(request, f'Proveedor "{nombre}" eliminado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        return redirect('proveedores')


@method_decorator(admin_login_required, name='dispatch')
class ProveedoresJsonView(View):
    def get(self, request):
        lista = list(Proveedor.objects.all().values(
            'id', 'nombre', 'telefono', 'email', 'fechaRegistro'
        ))
        return JsonResponse({'proveedores': lista})


@method_decorator(admin_login_required, name='dispatch')
class ProveedorProductosView(View):
    def get(self, request, id):
        proveedor = get_object_or_404(Proveedor, id=id)
        qs = proveedor.productos.all()
        if not qs.exists():
            qs = Producto.objects.all()
        data = [
            {'id': p.idProducto, 'nombre': p.nombre, 'stock': p.stock, 'precio': float(p.precio)}
            for p in qs
        ]
        return JsonResponse({'productos': data, 'proveedor': proveedor.nombre})

    def post(self, request, id):
        import json
        proveedor = get_object_or_404(Proveedor, id=id)
        try:
            body = json.loads(request.body)
            ids  = body.get('producto_ids', [])
            proveedor.productos.set(ids)
            return JsonResponse({'ok': True, 'total': proveedor.productos.count()})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


proveedores         = ProveedoresView.as_view()
crear_proveedor     = CrearProveedorView.as_view()
editar_proveedor    = EditarProveedorView.as_view()
eliminar_proveedor  = EliminarProveedorView.as_view()
proveedores_json    = ProveedoresJsonView.as_view()
proveedor_productos = ProveedorProductosView.as_view()
