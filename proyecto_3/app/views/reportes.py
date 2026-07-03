from django.views import View
from django.http import HttpResponse
from app.models import Proveedor, Producto, Cliente, Venta, Compra
from app.utils import exportar_pdf, exportar_excel, exportar_pdf_general, exportar_excel_general
from datetime import datetime


# ====== PROVEEDORES ======

class ExportarProveedoresPDF(View):
    def get(self, request):
        proveedores = Proveedor.objects.all().order_by('nombre')
        columnas    = ['ID', 'Nombre', 'Teléfono', 'Email', 'Costo Envío', 'Fecha Registro']
        datos       = [
            (p.id, p.nombre, p.telefono, p.email,
             f'${p.envio:,}', p.fechaRegistro.strftime('%d/%m/%Y'))
            for p in proveedores
        ]
        return exportar_pdf(
            titulo         = 'REPORTE DE PROVEEDORES',
            columnas       = columnas,
            datos          = datos,
            nombre_archivo = f'Reporte_Proveedores_{datetime.now().strftime("%d_%m_%Y")}',
        )


class ExportarProveedoresExcel(View):
    def get(self, request):
        proveedores = Proveedor.objects.all().order_by('nombre')
        columnas    = ['ID', 'Nombre', 'Teléfono', 'Email', 'Costo Envío', 'Fecha Registro']
        datos       = [
            (p.id, p.nombre, p.telefono, p.email,
             p.envio, p.fechaRegistro.strftime('%d/%m/%Y'))
            for p in proveedores
        ]
        return exportar_excel(
            titulo         = 'REPORTE DE PROVEEDORES',
            columnas       = columnas,
            datos          = datos,
            nombre_archivo = f'Reporte_Proveedores_{datetime.now().strftime("%d_%m_%Y")}',
        )


# ====== PRODUCTOS ======
# ─── CORRECCIÓN: se agregaron las columnas Marca, Tipo y Unidad.
# La versión anterior solo exportaba ID, Nombre, Precio y Stock,
# perdiendo información clave del producto.

class ExportarProductosPDF(View):
    def get(self, request):
        productos = Producto.objects.select_related('idMarca', 'idTipo', 'idUnidad').all().order_by('nombre')
        columnas  = ['ID', 'Nombre', 'Marca', 'Tipo', 'Unidad', 'Precio', 'Stock']
        datos     = [
            (p.idProducto, p.nombre,
             p.idMarca.nombreMarca,
             p.idTipo.nombre_tipo,
             p.idUnidad.nombre_unidad,
             f'${float(p.precio):,.2f}',
             p.stock)
            for p in productos
        ]
        return exportar_pdf(
            titulo         = 'REPORTE DE PRODUCTOS',
            columnas       = columnas,
            datos          = datos,
            nombre_archivo = f'Reporte_Productos_{datetime.now().strftime("%d_%m_%Y")}',
        )


class ExportarProductosExcel(View):
    def get(self, request):
        productos = Producto.objects.select_related('idMarca', 'idTipo', 'idUnidad').all().order_by('nombre')
        columnas  = ['ID', 'Nombre', 'Marca', 'Tipo', 'Unidad', 'Precio', 'Stock']
        datos     = [
            (p.idProducto, p.nombre,
             p.idMarca.nombreMarca,
             p.idTipo.nombre_tipo,
             p.idUnidad.nombre_unidad,
             float(p.precio),
             p.stock)
            for p in productos
        ]
        return exportar_excel(
            titulo         = 'REPORTE DE PRODUCTOS',
            columnas       = columnas,
            datos          = datos,
            nombre_archivo = f'Reporte_Productos_{datetime.now().strftime("%d_%m_%Y")}',
        )


# ====== CLIENTES ======

class ExportarClientesPDF(View):
    def get(self, request):
        clientes = Cliente.objects.all().order_by('nombre')
        columnas = ['ID', 'Nombre', 'Documento', 'Teléfono', 'Email', 'Dirección', 'Estado', 'Registro']
        datos    = [
            (c.id, c.nombre, c.documento, c.telefono, c.email,
             c.direccion or '—', c.estado.capitalize(),
             c.fechaRegistro.strftime('%d/%m/%Y'))
            for c in clientes
        ]
        return exportar_pdf(
            titulo         = 'REPORTE DE CLIENTES',
            columnas       = columnas,
            datos          = datos,
            nombre_archivo = f'Reporte_Clientes_{datetime.now().strftime("%d_%m_%Y")}',
        )


class ExportarClientesExcel(View):
    def get(self, request):
        clientes = Cliente.objects.all().order_by('nombre')
        columnas = ['ID', 'Nombre', 'Documento', 'Teléfono', 'Email', 'Dirección', 'Estado', 'Registro']
        datos    = [
            (c.id, c.nombre, c.documento, c.telefono, c.email,
             c.direccion or '—', c.estado.capitalize(),
             c.fechaRegistro.strftime('%d/%m/%Y'))
            for c in clientes
        ]
        return exportar_excel(
            titulo         = 'REPORTE DE CLIENTES',
            columnas       = columnas,
            datos          = datos,
            nombre_archivo = f'Reporte_Clientes_{datetime.now().strftime("%d_%m_%Y")}',
        )


# ====== VENTAS ======

class ExportarVentasPDF(View):
    def get(self, request):
        ventas   = Venta.objects.prefetch_related('detalles').all().order_by('-fecha')
        columnas = ['ID', 'Cliente', 'Fecha', 'Total', 'Estado']
        datos    = [
            (f'V{v.id:03d}', v.cliente,
             v.fecha.strftime('%d/%m/%Y %H:%M'),
             f'${float(v.total):,.2f}',
             v.estado)
            for v in ventas
        ]
        return exportar_pdf(
            titulo         = 'REPORTE DE VENTAS',
            columnas       = columnas,
            datos          = datos,
            nombre_archivo = f'Reporte_Ventas_{datetime.now().strftime("%d_%m_%Y")}',
        )


class ExportarVentasExcel(View):
    def get(self, request):
        ventas   = Venta.objects.prefetch_related('detalles').all().order_by('-fecha')
        columnas = ['ID', 'Cliente', 'Fecha', 'Total', 'Estado']
        datos    = [
            (f'V{v.id:03d}', v.cliente,
             v.fecha.strftime('%d/%m/%Y %H:%M'),
             float(v.total),
             v.estado)
            for v in ventas
        ]
        return exportar_excel(
            titulo         = 'REPORTE DE VENTAS',
            columnas       = columnas,
            datos          = datos,
            nombre_archivo = f'Reporte_Ventas_{datetime.now().strftime("%d_%m_%Y")}',
        )


# ====== COMPRAS ======

class ExportarComprasPDF(View):
    def get(self, request):
        compras  = Compra.objects.select_related('Producto', 'Proveedor', 'usuario').all().order_by('-fechaCompra')
        columnas = ['ID', 'Fecha', 'Producto', 'Proveedor', 'Cantidad', 'Precio Unit.', 'Total', 'Estado']
        datos    = [
            (f'C{c.idCompra:03d}',
             c.fechaCompra.strftime('%d/%m/%Y'),
             c.Producto.nombre      if c.Producto  else '—',
             c.Proveedor.nombre     if c.Proveedor else '—',
             c.cantidad,
             f'${float(c.precio_unitario):,.2f}',
             f'${float(c.total):,.2f}',
             c.estado)
            for c in compras
        ]
        return exportar_pdf(
            titulo         = 'REPORTE DE COMPRAS',
            columnas       = columnas,
            datos          = datos,
            nombre_archivo = f'Reporte_Compras_{datetime.now().strftime("%d_%m_%Y")}',
        )


class ExportarComprasExcel(View):
    def get(self, request):
        compras  = Compra.objects.select_related('Producto', 'Proveedor', 'usuario').all().order_by('-fechaCompra')
        columnas = ['ID', 'Fecha', 'Producto', 'Proveedor', 'Cantidad', 'Precio Unit.', 'Total', 'Estado']
        datos    = [
            (f'C{c.idCompra:03d}',
             c.fechaCompra.strftime('%d/%m/%Y'),
             c.Producto.nombre      if c.Producto  else '—',
             c.Proveedor.nombre     if c.Proveedor else '—',
             c.cantidad,
             float(c.precio_unitario),
             float(c.total),
             c.estado)
            for c in compras
        ]
        return exportar_excel(
            titulo         = 'REPORTE DE COMPRAS',
            columnas       = columnas,
            datos          = datos,
            nombre_archivo = f'Reporte_Compras_{datetime.now().strftime("%d_%m_%Y")}',
        )

# ====== REPORTE GENERAL (todos los módulos combinados) ======

def _secciones_generales():
    """Arma las secciones (una por módulo) reutilizando el mismo formato
    de columnas/datos que ya usa cada exportación individual."""
    productos = Producto.objects.select_related('idMarca', 'idTipo', 'idUnidad').all().order_by('nombre')
    clientes  = Cliente.objects.all().order_by('nombre')
    ventas    = Venta.objects.prefetch_related('detalles').all().order_by('-fecha')
    proveedores = Proveedor.objects.all().order_by('nombre')
    compras   = Compra.objects.select_related('Producto', 'Proveedor', 'usuario').all().order_by('-fechaCompra')

    return [
        {
            'titulo': 'Productos',
            'columnas': ['ID', 'Nombre', 'Marca', 'Tipo', 'Unidad', 'Precio', 'Stock'],
            'datos': [
                (p.idProducto, p.nombre, p.idMarca.nombreMarca, p.idTipo.nombre_tipo,
                 p.idUnidad.nombre_unidad, float(p.precio), p.stock)
                for p in productos
            ],
        },
        {
            'titulo': 'Clientes',
            'columnas': ['ID', 'Nombre', 'Documento', 'Teléfono', 'Email', 'Dirección', 'Estado', 'Registro'],
            'datos': [
                (c.id, c.nombre, c.documento, c.telefono, c.email,
                 c.direccion or '—', c.estado.capitalize(), c.fechaRegistro.strftime('%d/%m/%Y'))
                for c in clientes
            ],
        },
        {
            'titulo': 'Ventas',
            'columnas': ['ID', 'Cliente', 'Fecha', 'Total', 'Estado'],
            'datos': [
                (f'V{v.id:03d}', v.cliente, v.fecha.strftime('%d/%m/%Y %H:%M'), float(v.total), v.estado)
                for v in ventas
            ],
        },
        {
            'titulo': 'Proveedores',
            'columnas': ['ID', 'Nombre', 'Teléfono', 'Email', 'Costo Envío', 'Fecha Registro'],
            'datos': [
                (p.id, p.nombre, p.telefono, p.email, p.envio, p.fechaRegistro.strftime('%d/%m/%Y'))
                for p in proveedores
            ],
        },
        {
            'titulo': 'Compras',
            'columnas': ['ID', 'Fecha', 'Producto', 'Proveedor', 'Cantidad', 'Precio Unit.', 'Total', 'Estado'],
            'datos': [
                (f'C{c.idCompra:03d}', c.fechaCompra.strftime('%d/%m/%Y'),
                 c.Producto.nombre if c.Producto else '—',
                 c.Proveedor.nombre if c.Proveedor else '—',
                 c.cantidad, float(c.precio_unitario), float(c.total), c.estado)
                for c in compras
            ],
        },
    ]


class ExportarGeneralPDF(View):
    def get(self, request):
        return exportar_pdf_general(
            titulo         = 'REPORTE GENERAL',
            secciones      = _secciones_generales(),
            nombre_archivo = f'Reporte_General_{datetime.now().strftime("%d_%m_%Y")}',
        )


class ExportarGeneralExcel(View):
    def get(self, request):
        return exportar_excel_general(
            secciones      = _secciones_generales(),
            nombre_archivo = f'Reporte_General_{datetime.now().strftime("%d_%m_%Y")}',
        )