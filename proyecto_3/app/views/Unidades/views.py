"""Vistas para gestión de unidades de medida"""
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.urls import reverse
from app.decorators import admin_login_required
from app.models import unidad_medida, Producto

# Abreviaturas permitidas (valores válidos del select)
ABREVIATURAS_VALIDAS = {'kg','g','mg','t','lb','oz','l','ml','kl','cl','m','cm','mm','un','doc','paq','caj','bol','bot','lta','por'}

# Abreviaturas estándar por unidad
ABREVIATURAS = {
    'kilogramo': 'kg', 'gramo': 'g', 'miligramo': 'mg', 'tonelada': 't',
    'libra': 'lb', 'onza': 'oz', 'litro': 'l', 'mililitro': 'ml',
    'kilolitro': 'kl', 'centilitro': 'cl', 'metro': 'm', 'centímetro': 'cm', 'milímetro': 'mm',
    'unidad': 'un', 'docena': 'doc', 'paquete': 'paq', 'caja': 'caj',
    'bolsa': 'bol', 'botella': 'bot', 'lata': 'lta', 'porción': 'por'
}


@method_decorator(admin_login_required, name='dispatch')
class UnidadesView(View):
    def get(self, request):
        return render(request, 'Unidad_medida/unidades.html', {'unidades': unidad_medida.objects.all()})


@method_decorator(admin_login_required, name='dispatch')
class CrearUnidadView(View):
    def post(self, request):
        nombre       = request.POST.get('nombre_unidad', '').strip()
        abreviatura  = request.POST.get('abreviatura', '').strip().lower()

        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
        elif len(nombre) < 2:
            messages.error(request, 'El nombre es muy corto.')
        # El regex ahora permite: letras, números, espacios y puntos.
        elif not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚüÜñÑ .]+$', nombre):
            messages.error(request, 'El nombre contiene caracteres no permitidos.')
        elif not abreviatura or abreviatura not in ABREVIATURAS_VALIDAS:
            messages.error(request, 'La abreviatura no es válida o no fue seleccionada.')
        elif unidad_medida.objects.filter(nombre_unidad__iexact=nombre).exists():
            messages.error(request, f'Ya existe una unidad llamada "{nombre}".')
        else:
            unidad_medida.objects.create(nombre_unidad=nombre, abreviatura=abreviatura)
            messages.success(request, f'Unidad "{nombre}" creada exitosamente.')
            return redirect(reverse('productos') + '?abrir_modal=1')
        return redirect('unidades')


@method_decorator(admin_login_required, name='dispatch')
class EliminarUnidadView(View):
    def post(self, request, id):
        unidad = get_object_or_404(unidad_medida, idUnidad=id)
        if Producto.objects.filter(idUnidad=unidad).exists():
            messages.error(request, f'No se puede eliminar "{unidad.nombre_unidad}": tiene productos asociados.')
        else:
            nombre = unidad.nombre_unidad
            unidad.delete()
            messages.success(request, f'Unidad "{nombre}" eliminada.')
        return redirect('unidades')


unidades        = UnidadesView.as_view()
crear_unidad    = CrearUnidadView.as_view()
eliminar_unidad = EliminarUnidadView.as_view()