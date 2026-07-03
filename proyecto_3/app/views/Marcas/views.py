"""Vistas para gestión de marcas"""
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse
from app.decorators import admin_login_required
from app.models import Marca, Producto


@method_decorator(admin_login_required, name='dispatch')
class MarcasView(View):
    def get(self, request):
        return render(request, 'Marcas/marcas.html', {'marcas': Marca.objects.all()})


@method_decorator(admin_login_required, name='dispatch')
class CrearMarcaView(View):
    def post(self, request):
        nombre = request.POST.get('nombreMarca', '').strip()
        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
        elif len(nombre) < 2:
            messages.error(request, 'El nombre debe tener al menos 2 letras.')
        elif len(nombre) > 100:
            messages.error(request, 'El nombre no puede superar 100 letras.')
        elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', nombre):
            messages.error(request, 'El nombre solo puede contener letras y espacios.')
        elif Marca.objects.filter(nombreMarca__iexact=nombre).exists():
            messages.error(request, f'Ya existe una marca llamada "{nombre}".')
        else:
            Marca.objects.create(nombreMarca=nombre)
            messages.success(request, f'Marca "{nombre}" creada exitosamente.')
            return redirect(reverse('productos') + '?abrir_modal=1')
        return redirect('marcas')


@method_decorator(admin_login_required, name='dispatch')
class EliminarMarcaView(View):
    def post(self, request, id):
        marca = get_object_or_404(Marca, idMarca=id)
        if Producto.objects.filter(idMarca=marca).exists():
            messages.error(request, f'No se puede eliminar "{marca.nombreMarca}": tiene productos asociados.')
        else:
            nombre = marca.nombreMarca
            marca.delete()
            messages.success(request, f'Marca "{nombre}" eliminada.')
        return redirect('marcas')


marcas         = MarcasView.as_view()
crear_marca    = CrearMarcaView.as_view()
eliminar_marca = EliminarMarcaView.as_view()
