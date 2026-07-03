"""Vistas para gestión de productos"""
import re
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from app.decorators import admin_login_required
from app.models import Producto, Marca, TipoProductos, unidad_medida


def _contexto_productos(query='', form_data=None):
    """Construye el contexto base. form_data preserva valores del modal si hay error."""
    lista = Producto.objects.all()
    if query:
        lista = lista.filter(nombre__icontains=query)
    return {
        'productos': lista,
        'marcas':    Marca.objects.all(),
        'tipos':     TipoProductos.objects.all(),
        'unidades':  unidad_medida.objects.all(),
        'form_data': form_data or {},
    }


@method_decorator(admin_login_required, name='dispatch')
class ProductosView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        return render(request, 'Productos/productos.html', _contexto_productos(query))


@method_decorator(admin_login_required, name='dispatch')
class CrearProductoView(View):
    def post(self, request):
        form_data = {
            'nombre':   request.POST.get('nombre', '').strip(),
            'precio':   request.POST.get('precio', '').strip(),
            'stock':    request.POST.get('stock', '').strip(),
            'idMarca':  request.POST.get('idMarca', ''),
            'idTipo':   request.POST.get('idTipo', ''),
            'idUnidad': request.POST.get('idUnidad', ''),
            'fecha_vencimiento': request.POST.get('fecha_vencimiento', '').strip(),
        }

        def error(msg):
            messages.error(request, msg)
            ctx = _contexto_productos(form_data=form_data)
            ctx['abrir_modal_agregar'] = True
            return render(request, 'Productos/productos.html', ctx)

        nombre   = form_data['nombre']
        precio   = form_data['precio']
        stock    = form_data['stock']
        idMarca  = form_data['idMarca']
        idTipo   = form_data['idTipo']
        idUnidad = form_data['idUnidad']

        if not nombre:
            return error('El nombre es obligatorio.')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', nombre):
            return error('El nombre solo puede contener letras y espacios.')
        if Marca.objects.filter(nombreMarca__iexact=nombre).exists():
            return error(f'"{nombre}" ya existe como Marca.')
        if TipoProductos.objects.filter(nombre_tipo__iexact=nombre).exists():
            return error(f'"{nombre}" ya existe como Tipo de producto.')
        if unidad_medida.objects.filter(nombre_unidad__iexact=nombre).exists():
            return error(f'"{nombre}" ya existe como Unidad de medida.')
        if Producto.objects.filter(nombre__iexact=nombre, idMarca=idMarca, idTipo=idTipo).exists():
            return error(f'Ya existe un producto "{nombre}" con esa marca y tipo.')

        try:
            precio_val = float(precio.replace(',', '.'))
            if precio_val < 1 or precio_val > 800000:
                raise ValueError
        except ValueError:
            return error('El precio debe ser un número entre 1 y 800.000.')

        if not stock.isdigit() or int(stock) < 0 or int(stock) > 1000:
            return error('El stock debe ser un número entre 0 y 1.000.')

        codigo_barras = request.POST.get('codigo_barras', '').strip()
        fecha_vencimiento = request.POST.get('fecha_vencimiento', '').strip() or None

        try:
            Producto.objects.create(
                nombre=nombre,
                precio=precio_val,
                stock=int(stock),
                idMarca=get_object_or_404(Marca, idMarca=idMarca),
                idTipo=get_object_or_404(TipoProductos, idTipo=idTipo),
                idUnidad=get_object_or_404(unidad_medida, idUnidad=idUnidad),
                codigo_barras=codigo_barras,
                fecha_vencimiento=fecha_vencimiento,
            )
            messages.success(request, f'Producto "{nombre}" creado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al crear el producto: {str(e)}')

        return redirect('productos')


@method_decorator(admin_login_required, name='dispatch')
class EditarProductoView(View):
    def post(self, request, id):
        producto = get_object_or_404(Producto, idProducto=id)
        nombre   = request.POST.get('nombre', '').strip()
        precio   = request.POST.get('precio', '').strip()
        stock    = request.POST.get('stock', '').strip()
        idMarca  = request.POST.get('idMarca')
        idTipo   = request.POST.get('idTipo')
        idUnidad = request.POST.get('idUnidad')

        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
            return redirect('productos')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', nombre):
            messages.error(request, 'El nombre solo puede contener letras y espacios.')
            return redirect('productos')
        if Marca.objects.filter(nombreMarca__iexact=nombre).exists():
            messages.error(request, f'"{nombre}" ya existe como Marca.')
            return redirect('productos')
        if TipoProductos.objects.filter(nombre_tipo__iexact=nombre).exists():
            messages.error(request, f'"{nombre}" ya existe como Tipo de producto.')
            return redirect('productos')
        if unidad_medida.objects.filter(nombre_unidad__iexact=nombre).exists():
            messages.error(request, f'"{nombre}" ya existe como Unidad de medida.')
            return redirect('productos')
        if Producto.objects.filter(nombre__iexact=nombre, idMarca=idMarca, idTipo=idTipo).exclude(idProducto=id).exists():
            messages.error(request, f'Ya existe un producto "{nombre}" con esa marca y tipo.')
            return redirect('productos')

        try:
            precio_val = float(precio.replace(',', '.'))
        except ValueError:
            messages.error(request, 'El precio debe ser un número válido.')
            return redirect('productos')
        if precio_val < 1 or precio_val > 800000:
            messages.error(request, 'El precio debe ser un número entre 1 y 800.000.')
            return redirect('productos')
        if not stock.isdigit() or int(stock) < 0 or int(stock) > 1000:
            messages.error(request, 'El stock debe ser un número entre 0 y 1.000.')
            return redirect('productos')

        producto.nombre   = nombre
        producto.precio   = precio_val
        producto.stock    = int(stock)
        producto.idMarca  = get_object_or_404(Marca, idMarca=idMarca)
        producto.idTipo   = get_object_or_404(TipoProductos, idTipo=idTipo)
        producto.idUnidad = get_object_or_404(unidad_medida, idUnidad=idUnidad)
        producto.fecha_vencimiento = request.POST.get('fecha_vencimiento', '').strip() or None
        producto.save()
        messages.success(request, f'Producto "{nombre}" actualizado correctamente.')
        return redirect('productos')


@method_decorator(admin_login_required, name='dispatch')
class EliminarProductoView(View):
    def post(self, request, id):
        try:
            producto = get_object_or_404(Producto, idProducto=id)
            nombre   = producto.nombre
            producto.delete()
            messages.success(request, f'Producto "{nombre}" eliminado correctamente.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        return redirect('productos')


productos         = ProductosView.as_view()
crear_producto    = CrearProductoView.as_view()
editar_producto   = EditarProductoView.as_view()
eliminar_producto = EliminarProductoView.as_view()


@admin_login_required
@require_GET
def buscar_codigo_barras(request):
    codigo = request.GET.get('codigo', '').strip()
    if not codigo:
        return JsonResponse({'error': 'Código vacío'}, status=400)
    try:
        producto = Producto.objects.get(codigo_barras=codigo)
        return JsonResponse({
            'id':     producto.idProducto,
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'stock':  producto.stock,
        })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)


@admin_login_required
@require_POST
def actualizar_stock_escaner(request):
    try:
        data     = json.loads(request.body)
        producto = Producto.objects.get(idProducto=data.get('id'))
        cantidad = int(data.get('cantidad', 0))
        producto.stock += cantidad
        producto.save()
        return JsonResponse({'ok': True, 'stock': producto.stock})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# ══════════════════════════════════════════════════════════════
# ESCÁNER — buscar en BD + Open Food Facts
# ══════════════════════════════════════════════════════════════
import urllib.request
import urllib.error

@admin_login_required
@require_GET
def buscar_codigo_escaner(request):
    """
    1. Si modo=nombre: busca por nombre (para búsqueda manual en escáner de ventas)
    2. Busca en la BD propia por código de barras
    3. Si no existe, consulta Open Food Facts
    4. Devuelve datos para el modal
    """
    codigo = request.GET.get('codigo', '').strip()
    modo   = request.GET.get('modo', '').strip()

    if not codigo:
        return JsonResponse({'error': 'Código vacío'}, status=400)

    # ── 0. Búsqueda por nombre (modo=nombre) ──
    if modo == 'nombre':
        qs = Producto.objects.filter(nombre__icontains=codigo)[:8]
        resultados = [
            {'id': p.idProducto, 'nombre': p.nombre, 'precio': float(p.precio), 'stock': p.stock, 'codigo': p.codigo_barras or ''}
            for p in qs
        ]
        return JsonResponse({'estado': 'lista', 'resultados': resultados})

    # ── 1. Buscar en BD propia por código ──
    try:
        p = Producto.objects.get(codigo_barras=codigo)
        return JsonResponse({
            'estado':   'encontrado',
            'id':       p.idProducto,
            'nombre':   p.nombre,
            'precio':   float(p.precio),
            'stock':    p.stock,
            'codigo':   codigo,
        })
    except Producto.DoesNotExist:
        pass

    # ── 2. Consultar Open Food Facts ──
    nombre_sugerido = ''
    marca_sugerida  = ''
    try:
        url = f'https://world.openfoodfacts.org/api/v0/product/{codigo}.json'
        req = urllib.request.Request(url, headers={'User-Agent': 'TiendaElDespecho/1.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        if data.get('status') == 1:
            prod = data.get('product', {})
            nombre_sugerido = (
                prod.get('product_name_es') or
                prod.get('product_name') or
                prod.get('abbreviated_product_name') or ''
            )
            marca_sugerida = prod.get('brands', '').split(',')[0].strip()
    except Exception:
        pass

    return JsonResponse({
        'estado':          'no_encontrado',
        'codigo':          codigo,
        'nombre_sugerido': nombre_sugerido,
        'marca_sugerida':  marca_sugerida,
    })


@admin_login_required
@require_POST
def actualizar_stock_desde_escaner(request):
    """Suma cantidad al stock del producto encontrado"""
    try:
        data     = json.loads(request.body)
        producto = Producto.objects.get(idProducto=data.get('id'))
        cantidad = int(data.get('cantidad', 1))
        if cantidad < 1:
            return JsonResponse({'error': 'Cantidad inválida'}, status=400)
        producto.stock += cantidad
        producto.save()
        return JsonResponse({'ok': True, 'stock_nuevo': producto.stock, 'nombre': producto.nombre})
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@admin_login_required
@require_GET
def listado_productos_json(request):
    """Devuelve todos los productos como JSON. Usado por el modal de asignación de proveedores."""
    qs = Producto.objects.all().values('idProducto', 'nombre', 'stock', 'precio')
    data = [
        {'id': p['idProducto'], 'nombre': p['nombre'], 'stock': p['stock'], 'precio': float(p['precio'])}
        for p in qs
    ]
    return JsonResponse({'productos': data})

