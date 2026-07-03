"""
config/urls.py — ÚNICO archivo de rutas del proyecto.
app/urls.py está vacío a propósito: las rutas viven aquí.
"""
from django.urls import path, include
from django.contrib import admin
from app.views.IA import views as ia_views 

from app.views.Auth          import views as auth_views
from app.views.Index         import views as index_views
from app.views.Productos     import views as productos_views
from app.views.Clientes      import views as clientes_views
from app.views.Proveedores   import views as proveedores_views
from app.views.Compras       import views as compras_views
from app.views.Ventas        import views as ventas_views
from app.views.Reportes      import views as reportes_views
from app.views               import reportes as exportar_views
from app.views.Marcas        import views as marcas_views
from app.views.Tipo_producto import views as tipos_views
from app.views.Unidades      import views as unidades_views
from app.views               import backup as backup_views


urlpatterns = [
    # Django admin (necesario para la app usuarios)
    path('admin/', admin.site.urls),

    # ── Gestión de usuarios (solo superadmin) ──────────────────────
    path('usuarios/', include('usuarios.urls')),

    # ── Inicio ─────────────────────────────────────────────────────
    path('', index_views.index, name='inicio'),

    # ── Auth ───────────────────────────────────────────────────────
    path('login/',  auth_views.login_view,  name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('login/enviar-codigo/',       auth_views.send_recovery_code,     name='send_recovery_code'),
    path('login/confirmar-codigo/',    auth_views.validate_recovery_code,  name='validate_recovery_code'),
    path('login/resetear-contrasena/', auth_views.reset_password,          name='reset_password'),

    # ── Notificaciones ─────────────────────────────────────────────
    path('notificaciones/data/',  index_views.notificaciones_data, name='notificaciones_data'),
    path('notificaciones/limpiar/', index_views.limpiar_notificaciones, name='limpiar_notificaciones'),
    path('notificaciones/leer/<int:id>/', index_views.marcar_leida_notificacion, name='marcar_leida_notificacion'),
    path('notificaciones/eliminar/<int:id>/', index_views.eliminar_notificacion, name='eliminar_notificacion'),
    path('notificaciones/historial/',           index_views.historial_notificaciones, name='historial_notificaciones'),

    # ── Productos ──────────────────────────────────────────────────
    path('productos/',                    productos_views.productos,        name='productos'),
    path('productos/crear/',              productos_views.crear_producto,   name='crear_producto'),
    path('productos/editar/<int:id>/',    productos_views.editar_producto,  name='editar_producto'),
    path('productos/eliminar/<int:id>/',  productos_views.eliminar_producto, name='eliminar_producto'),
    # ── Escáner de código de barras ────────────────────────────────
    path('productos/buscar-codigo/',         productos_views.buscar_codigo_barras,    name='buscar_codigo_barras'),
    path('productos/actualizar-stock-escaner/', productos_views.actualizar_stock_escaner, name='actualizar_stock_escaner'),
    path('productos/buscar-escaner/',           productos_views.buscar_codigo_escaner,      name='buscar_codigo_escaner'),
    path('api/productos/listado/',               productos_views.listado_productos_json,     name='listado_productos_json'),
    path('productos/actualizar-stock-nuevo/',   productos_views.actualizar_stock_desde_escaner, name='actualizar_stock_desde_escaner'),
    # ──────────────────────────────────────────────────────────────
    path('reporte/productos/pdf',   exportar_views.ExportarProductosPDF.as_view(),   name='exportar_productos_pdf'),
    path('reporte/productos/excel', exportar_views.ExportarProductosExcel.as_view(), name='exportar_productos_excel'),

    # ── Marcas ─────────────────────────────────────────────────────
    path('marcas/',                   marcas_views.marcas,       name='marcas'),
    path('marcas/crear/',             marcas_views.crear_marca,  name='crear_marca'),
    path('marcas/eliminar/<int:id>/', marcas_views.eliminar_marca, name='eliminar_marca'),

    # ── Tipos de producto ──────────────────────────────────────────
    path('tipos/',                   tipos_views.tipos,        name='tipos'),
    path('tipos/crear/',             tipos_views.crear_tipo,   name='crear_tipo'),
    path('tipos/eliminar/<int:id>/', tipos_views.eliminar_tipo, name='eliminar_tipo'),

    # ── Unidades de medida ─────────────────────────────────────────
    path('unidades/',                   unidades_views.unidades,        name='unidades'),
    path('unidades/crear/',             unidades_views.crear_unidad,    name='crear_unidad'),
    path('unidades/eliminar/<int:id>/', unidades_views.eliminar_unidad, name='eliminar_unidad'),

    # ── Clientes ───────────────────────────────────────────────────
    path('clientes/',                   clientes_views.clientes,        name='clientes'),
    path('clientes/crear/',             clientes_views.crear_cliente,   name='crear_cliente'),
    path('clientes/editar/<int:id>/',   clientes_views.editar_cliente,  name='editar_cliente'),
    path('clientes/eliminar/<int:id>/', clientes_views.eliminar_cliente, name='eliminar_cliente'),
    path('reporte/clientes/pdf',   exportar_views.ExportarClientesPDF.as_view(),   name='exportar_clientes_pdf'),
    path('reporte/clientes/excel', exportar_views.ExportarClientesExcel.as_view(), name='exportar_clientes_excel'),

    # ── Ventas ─────────────────────────────────────────────────────
    path('ventas/',                      ventas_views.ventas,           name='ventas'),
    path('ventas/crear/',                ventas_views.crear_venta,      name='crear_venta'),
    path('ventas/detalle/<int:id>/',     ventas_views.detalle_venta,    name='detalle_venta'),
    path('ventas/detalle/<int:id>/devolucion/', ventas_views.crear_devolucion_venta, name='crear_devolucion_venta'),
    path('ventas/editar/<int:id>/',      ventas_views.editar_venta,     name='editar_venta'),
    path('ventas/completar/<int:id>/',   ventas_views.completar_venta,  name='completar_venta'),
    path('ventas/eliminar/<int:id>/',    ventas_views.eliminar_venta,   name='eliminar_venta'),
    path('ventas/estadisticas/',         ventas_views.estadisticas_ventas, name='estadisticas_ventas'),
    path('reporte/ventas/pdf',   exportar_views.ExportarVentasPDF.as_view(),   name='exportar_ventas_pdf'),
    path('reporte/ventas/excel', exportar_views.ExportarVentasExcel.as_view(), name='exportar_ventas_excel'),

    # ── Proveedores ────────────────────────────────────────────────
    path('proveedores/',                   proveedores_views.proveedores,        name='proveedores'),
    path('proveedores/crear/',             proveedores_views.crear_proveedor,    name='crear_proveedor'),
    path('proveedores/editar/<int:id>/',   proveedores_views.editar_proveedor,   name='editar_proveedor'),
    path('proveedores/eliminar/<int:id>/', proveedores_views.eliminar_proveedor, name='eliminar_proveedor'),
    path('proveedores/<int:id>/productos/', proveedores_views.proveedor_productos, name='proveedor_productos'),
    path('reporte/proveedores/pdf',   exportar_views.ExportarProveedoresPDF.as_view(),   name='exportar_proveedores_pdf'),
    path('reporte/proveedores/excel', exportar_views.ExportarProveedoresExcel.as_view(), name='exportar_proveedores_excel'),

    # ── Compras ────────────────────────────────────────────────────
    path('compras/',                   compras_views.compras,             name='compras'),
    path('compras/crear/',             compras_views.crear_compra,        name='crear_compra'),
    path('compras/editar/<int:id>/',   compras_views.modal_editar_compra, name='modal_editar_compra'),
    path('compras/eliminar/<int:id>/', compras_views.modal_eliminar_compra, name='modal_eliminar_compra'),
    path('compras/<int:id>/devolucion/', compras_views.crear_devolucion_compra, name='crear_devolucion_compra'),
    path('reporte/compras/pdf',   exportar_views.ExportarComprasPDF.as_view(),   name='exportar_compras_pdf'),
    path('reporte/compras/excel', exportar_views.ExportarComprasExcel.as_view(), name='exportar_compras_excel'),

    # ── Reportes ───────────────────────────────────────────────────
    path('reportes/',       reportes_views.reportes,      name='reportes'),
    path('reportes/data/',  reportes_views.reportes_data, name='reportes_data'),
    path('reporte/general/pdf',   exportar_views.ExportarGeneralPDF.as_view(),   name='exportar_general_pdf'),
    path('reporte/general/excel', exportar_views.ExportarGeneralExcel.as_view(), name='exportar_general_excel'),

    # ── Backup y Restauración ──────────────────────────────────────
    path('backup/',             backup_views.backup,           name='backup'),
    path('backup/restaurar/',   backup_views.restaurar_datos,  name='restaurar_datos'),
    # ── Asistente IA ───────────────────────────────────────────────
    path('ia/',      ia_views.ia_index, name='ia_index'),
    path('ia/chat/', ia_views.ia_chat,  name='ia_chat'),
]


from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
