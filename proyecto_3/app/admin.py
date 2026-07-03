from django.contrib import admin
from app.models import Producto, Marca, TipoProductos, unidad_medida

# Register your models here.
admin.site.register(Producto)
admin.site.register(Marca)
admin.site.register(TipoProductos)
admin.site.register(unidad_medida)
