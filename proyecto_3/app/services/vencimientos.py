"""
Servicio de alertas de vencimiento de productos.
Reutilizable en cualquier módulo (Compras, Ventas, Reportes, etc.)
que necesite mostrar avisos de productos vencidos o próximos a vencer.
"""
from django.utils import timezone
from app.models import Producto

# Días de anticipación para considerar un producto "próximo a vencer"
DIAS_ALERTA_VENCIMIENTO = 15
# Días de anticipación para considerar un producto "crítico" (vence muy pronto)
DIAS_CRITICO_VENCIMIENTO = 5


def productos_por_vencer(dias=DIAS_ALERTA_VENCIMIENTO):
    """
    Devuelve una lista de dicts con los productos vencidos o próximos a
    vencer dentro de `dias` días, ordenados por urgencia (los ya vencidos
    primero, luego los que vencen antes).

    Cada item: {
        'id', 'nombre', 'stock', 'fecha_vencimiento',
        'dias_restantes', 'estado' ('vencido' | 'critico' | 'proximo'),
        'label'
    }
    """
    hoy = timezone.now().date()
    limite = hoy + timezone.timedelta(days=dias)

    productos = (
        Producto.objects
        .filter(fecha_vencimiento__isnull=False, fecha_vencimiento__lte=limite)
        .order_by('fecha_vencimiento')
    )

    resultado = []
    for p in productos:
        dias_restantes = (p.fecha_vencimiento - hoy).days
        if dias_restantes < 0:
            estado, label = 'vencido', 'Vencido'
        elif dias_restantes <= DIAS_CRITICO_VENCIMIENTO:
            estado, label = 'critico', f'Vence en {dias_restantes} día{"s" if dias_restantes != 1 else ""}'
        else:
            estado, label = 'proximo', f'Vence en {dias_restantes} días'

        resultado.append({
            'id': p.idProducto,
            'nombre': p.nombre,
            'stock': p.stock,
            'fecha_vencimiento': p.fecha_vencimiento,
            'dias_restantes': dias_restantes,
            'estado': estado,
            'label': label,
        })

    return resultado


def contexto_alertas_vencimiento(dias=DIAS_ALERTA_VENCIMIENTO):
    """
    Devuelve el dict listo para mezclar en el contexto de cualquier vista
    que incluya el partial 'partials/alerta_vencimiento.html'.
    """
    alertas = productos_por_vencer(dias)
    return {
        'alertas_vencimiento': alertas,
        'alertas_vencimiento_vencidos': sum(1 for a in alertas if a['estado'] == 'vencido'),
    }
