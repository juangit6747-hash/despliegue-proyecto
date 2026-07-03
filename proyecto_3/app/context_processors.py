from django.utils import timezone
from app.models import NotificacionEmail

def notificaciones(request):
    if not request.user.is_authenticated:
        return {
            'notificaciones': [],
            'total_notificaciones': 0,
            'notif_stock_bajo': [],
            'notif_compras_vencer': [],
            'notif_total': 0,
        }

    notificaciones_lista = []

    try:
        notif_usuario = NotificacionEmail.objects.filter(
            usuario=request.user,
            leida=False
        ).order_by('-fecha_creacion')[:20]

        for notif in notif_usuario:
            url = '#'
            if 'compra' in notif.asunto.lower():
                url = '/compras/'
            elif 'venta' in notif.asunto.lower():
                url = '/ventas/'
            elif 'stock' in notif.asunto.lower() or 'agotado' in notif.asunto.lower():
                url = '/productos/'
            elif 'proveedor' in notif.asunto.lower():
                url = '/proveedores/'

            notificaciones_lista.append({
                'tipo': notif.tipo,
                'icono': {
                    'alerta': '⚠️',
                    'info': 'ℹ️',
                    'error': '❌',
                    'success': '✅',
                }.get(notif.tipo, '🔔'),
                'mensaje': notif.asunto,
                'url': url,
                'fecha': notif.fecha_creacion,
                'prioridad': 1 if notif.tipo == 'error' else 2 if notif.tipo == 'alerta' else 3,
                'notif_id': notif.id,
            })

    except Exception as e:
        print(f"Error en notificaciones: {e}")
        notificaciones_lista = []

    return {
        'notificaciones': notificaciones_lista,
        'total_notificaciones': len(notificaciones_lista),
        'notif_stock_bajo': [],
        'notif_compras_vencer': [],
        'notif_total': len(notificaciones_lista),
    }