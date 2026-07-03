"""Vistas para gestión de tipos de producto"""
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse
from app.decorators import admin_login_required
from app.models import TipoProductos, Producto


@method_decorator(admin_login_required, name='dispatch')
class TiposView(View):
    def get(self, request):
        return render(request, 'Tipo_producto/tipos.html', {'tipos': TipoProductos.objects.all()})


@method_decorator(admin_login_required, name='dispatch')
class CrearTipoView(View):
    def post(self, request):
        nombre = request.POST.get('nombre_tipo', '').strip()
        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
        elif len(nombre) < 2:
            messages.error(request, 'El nombre debe tener al menos 2 letras.')
        elif len(nombre) > 100:
            messages.error(request, 'El nombre no puede superar 100 letras.')
        elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', nombre):
            messages.error(request, 'El nombre solo puede contener letras y espacios.')
        elif TipoProductos.objects.filter(nombre_tipo__iexact=nombre).exists():
            messages.error(request, f'Ya existe un tipo llamado "{nombre}".')
        else:
            TipoProductos.objects.create(nombre_tipo=nombre)
            messages.success(request, f'Tipo "{nombre}" creado exitosamente.')
            return redirect(reverse('productos') + '?abrir_modal=1')
        return redirect('tipos')


@method_decorator(admin_login_required, name='dispatch')
class EliminarTipoView(View):
    def post(self, request, id):
        tipo = get_object_or_404(TipoProductos, idTipo=id)
        if Producto.objects.filter(idTipo=tipo).exists():
            messages.error(request, f'No se puede eliminar "{tipo.nombre_tipo}": tiene productos asociados.')
        else:
            nombre = tipo.nombre_tipo
            tipo.delete()
            messages.success(request, f'Tipo "{nombre}" eliminado.')
        return redirect('tipos')


tipos         = TiposView.as_view()
crear_tipo    = CrearTipoView.as_view()
eliminar_tipo = EliminarTipoView.as_view()
