"""Vistas para reportes"""
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from app.decorators import admin_login_required
from app.models import Producto, Cliente, Venta, Compra, Proveedor


@method_decorator(admin_login_required, name='dispatch')
class ReportesView(View):
    def get(self, request):
        # ── Fecha en UTC (las fechas en DB están guardadas en UTC) ──
        hoy        = timezone.now()
        mes_inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # ── KPIs ──
        total_productos   = Producto.objects.count()
        stock_bajo        = Producto.objects.filter(stock__lte=10).count()
        total_clientes    = Cliente.objects.count()
        total_proveedores = Proveedor.objects.count()
        total_compras     = Compra.objects.count()
        ventas_mes        = Venta.objects.filter(fecha__gte=mes_inicio, fecha__lte=hoy)
        total_ventas_mes  = ventas_mes.aggregate(t=Sum('total'))['t'] or 0
        transacciones_mes = ventas_mes.count()
        ingreso_total     = Venta.objects.aggregate(t=Sum('total'))['t'] or 0

        # ── PRODUCTOS ──
        productos = Producto.objects.select_related('idTipo', 'idMarca', 'idUnidad').all()
        max_stock = max((p.stock for p in productos), default=1) or 1
        productos_data = []
        for p in productos:
            if p.stock == 0:    estado, label = 'out', 'Sin stock'
            elif p.stock <= 10: estado, label = 'low', 'Bajo'
            else:               estado, label = 'ok',  'Normal'
            productos_data.append({
                'id': p.idProducto, 'nombre': p.nombre, 'precio': float(p.precio),
                'stock': p.stock, 'pct': int((p.stock / max_stock) * 100),
                'estado': estado, 'label': label,
            })

        graf_productos_labels  = [p['nombre'] for p in productos_data]
        graf_productos_stock   = [p['stock']  for p in productos_data]
        graf_productos_colores = [
            '#ef4444' if p['estado'] == 'out' else
            '#f59e0b' if p['estado'] == 'low' else '#22c55e'
            for p in productos_data
        ]

        # ── CLIENTES ──
        clientes_data = []
        for c in Cliente.objects.all():
            tc = Venta.objects.filter(cliente=c.nombre).aggregate(t=Sum('total'))['t'] or 0
            clientes_data.append({
                'id': c.id, 'nombre': c.nombre, 'email': c.email,
                'telefono': c.telefono, 'total_compras': float(tc), 'estado': c.estado,
            })

        top_clientes          = sorted(clientes_data, key=lambda x: x['total_compras'], reverse=True)[:8]
        graf_clientes_labels  = [c['nombre'] for c in top_clientes]
        graf_clientes_valores = [c['total_compras'] for c in top_clientes]
        clientes_activos      = sum(1 for c in clientes_data if c['estado'] == 'activo')
        clientes_inactivos    = len(clientes_data) - clientes_activos

        # ── VENTAS ──
        ventas_data = []
        for v in Venta.objects.prefetch_related('detalles').order_by('-fecha')[:50]:
            d = v.detalles.first()
            ventas_data.append({
                'id': v.id, 'cliente': v.cliente,
                'producto': d.producto_nombre if d else '-',
                'cantidad': d.cantidad if d else 0,
                'total': float(v.total), 'fecha': v.fecha, 'estado': v.estado,
            })

        ventas_por_dia = (
            Venta.objects
            .annotate(dia=TruncDate('fecha'))
            .values('dia').annotate(total_dia=Sum('total'))
            .order_by('dia')
        )[:14]
        graf_ventas_labels    = [str(v['dia']) for v in ventas_por_dia]
        graf_ventas_valores   = [float(v['total_dia']) for v in ventas_por_dia]
        ventas_completadas    = Venta.objects.filter(estado='Completada').count()
        ventas_pendientes     = Venta.objects.filter(estado='Pendiente').count()

        # ── PROVEEDORES ──
        proveedores_data = []
        for p in Proveedor.objects.all():
            nc = Compra.objects.filter(Proveedor=p).count()
            proveedores_data.append({
                'id': p.id, 'nombre': p.nombre, 'telefono': p.telefono,
                'email': p.email, 'envio': p.envio,
                'num_compras': nc, 'fecha': p.fechaRegistro,
            })

        graf_proveedores_labels  = [p['nombre']     for p in proveedores_data]
        graf_proveedores_valores = [p['num_compras'] for p in proveedores_data]

        # ── COMPRAS ──
        compras_data = []
        for c in Compra.objects.select_related('Producto', 'Proveedor', 'usuario').order_by('-fechaCompra')[:50]:
            compras_data.append({
                'id':        c.idCompra,
                'producto':  c.Producto.nombre      if c.Producto      else '-',
                'proveedor': c.Proveedor.nombre     if c.Proveedor     else '-',
                'admin':     c.usuario.get_full_name() or c.usuario.username if c.usuario else '-',
                'fecha':     str(c.fechaCompra),
                'estado':    c.estado,
            })

        compras_por_dia = (
            Compra.objects
            .values('fechaCompra').annotate(total_dia=Count('pk'))
            .order_by('fechaCompra')
        )[:14]
        graf_compras_labels  = [str(c['fechaCompra']) for c in compras_por_dia]
        graf_compras_valores = [c['total_dia']        for c in compras_por_dia]
        compras_completadas  = Compra.objects.filter(estado='Completada').count()
        compras_pendientes   = Compra.objects.filter(estado='Pendiente').count()

        productos_mini   = productos_data[:5]
        clientes_mini    = sorted(clientes_data, key=lambda x: x['total_compras'], reverse=True)[:5]
        ventas_mini      = ventas_data[:5]
        proveedores_mini = proveedores_data[:5]

        todas = []
        for v in Venta.objects.prefetch_related('detalles').order_by('-fecha')[:100]:
            d = v.detalles.first()
            desc = f"{d.producto_nombre} × {d.cantidad} — {v.cliente}" if d else v.cliente
            todas.append({
                'id': f"V{str(v.id).zfill(3)}", 'modulo': 'Venta', 'tipo': 'venta',
                'descripcion': desc, 'valor': float(v.total),
                'fecha': v.fecha, 'estado': v.estado,
            })
        for c in Compra.objects.select_related('Producto', 'Proveedor').order_by('-fechaCompra')[:50]:
            todas.append({
                'id': f"C{str(c.idCompra).zfill(3)}", 'modulo': 'Compra', 'tipo': 'compra',
                'descripcion': f"{c.Producto.nombre if c.Producto else '-'} — {c.Proveedor.nombre if c.Proveedor else '-'}",
                'valor': None, 'fecha': c.fechaCompra, 'estado': c.estado,
            })
        todas.sort(key=lambda x: str(x['fecha']), reverse=True)

        todas_fechas = sorted(set(graf_ventas_labels) | set(graf_compras_labels))

        ventas_por_fecha  = dict(zip(graf_ventas_labels,  graf_ventas_valores))
        compras_por_fecha = dict(zip(graf_compras_labels, graf_compras_valores))

        graf_todo_labels  = todas_fechas
        graf_todo_ventas  = [ventas_por_fecha.get(f, 0)  for f in todas_fechas]
        graf_todo_compras = [compras_por_fecha.get(f, 0) for f in todas_fechas]

        alertas_stock = [p for p in productos_data if p['estado'] in ('low', 'out')]

        context = {
            # KPIs
            'total_productos':  total_productos,  'stock_bajo':        stock_bajo,
            'total_clientes':   total_clientes,   'total_proveedores': total_proveedores,
            'total_compras':    total_compras,
            'total_ventas_mes': total_ventas_mes, 'transacciones_mes': transacciones_mes,
            'ingreso_total':    ingreso_total,
            # Tablas
            'productos_data':   productos_data,   'clientes_data':    clientes_data,
            'ventas_data':      ventas_data,       'proveedores_data': proveedores_data,
            'compras_data':     compras_data,
            # Mini
            'productos_mini':   productos_mini,   'clientes_mini':    clientes_mini,
            'ventas_mini':      ventas_mini,       'proveedores_mini': proveedores_mini,
            'todas':            todas,
            # Alertas
            'alertas_stock': alertas_stock,
            # Gráficas
            'graf_productos_labels':    graf_productos_labels,
            'graf_productos_stock':     graf_productos_stock,
            'graf_productos_colores':   graf_productos_colores,
            'graf_clientes_labels':     graf_clientes_labels,
            'graf_clientes_valores':    graf_clientes_valores,
            'clientes_activos':         clientes_activos,
            'clientes_inactivos':       clientes_inactivos,
            'graf_ventas_labels':       graf_ventas_labels,
            'graf_ventas_valores':      graf_ventas_valores,
            'ventas_completadas':       ventas_completadas,
            'ventas_pendientes':        ventas_pendientes,
            'graf_proveedores_labels':  graf_proveedores_labels,
            'graf_proveedores_valores': graf_proveedores_valores,
            'graf_compras_labels':      graf_compras_labels,
            'graf_compras_valores':     graf_compras_valores,
            'compras_completadas':      compras_completadas,
            'compras_pendientes':       compras_pendientes,
            'graf_todo_labels':         graf_todo_labels,
            'graf_todo_ventas':         graf_todo_ventas,
            'graf_todo_compras':        graf_todo_compras,
        }
        return render(request, 'Reportes/reportes.html', context)


@method_decorator(admin_login_required, name='dispatch')
class ReportesDataView(View):
    def get(self, request):
        # ── Fecha en UTC (las fechas en DB están guardadas en UTC) ──
        hoy        = timezone.now()
        mes_inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        ventas_mes        = Venta.objects.filter(fecha__gte=mes_inicio, fecha__lte=hoy)
        total_ventas_mes  = float(ventas_mes.aggregate(t=Sum('total'))['t'] or 0)
        transacciones_mes = ventas_mes.count()
        ingreso_total     = float(Venta.objects.aggregate(t=Sum('total'))['t'] or 0)
        stock_bajo        = Producto.objects.filter(stock__lte=10).count()

        ventas_por_dia = (
            Venta.objects.annotate(dia=TruncDate('fecha'))
            .values('dia').annotate(total_dia=Sum('total')).order_by('dia')
        )[:14]
        grafica_labels  = [str(v['dia']) for v in ventas_por_dia]
        grafica_valores = [float(v['total_dia']) for v in ventas_por_dia]

        alertas = [
            {'nombre': p.nombre, 'stock': p.stock, 'estado': 'out' if p.stock == 0 else 'low'}
            for p in Producto.objects.filter(stock__lte=10)
        ]

        return JsonResponse({
            'total_ventas_mes':  total_ventas_mes,
            'transacciones_mes': transacciones_mes,
            'ingreso_total':     ingreso_total,
            'stock_bajo':        stock_bajo,
            'grafica_labels':    grafica_labels,
            'grafica_valores':   grafica_valores,
            'alertas':           alertas,
        })


reportes      = ReportesView.as_view()
reportes_data = ReportesDataView.as_view()