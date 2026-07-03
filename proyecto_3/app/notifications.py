"""
Utilidades simples para notificaciones por correo a administradores.
Pensado para proyectos académicos: solución clara y fácil de explicar.
"""
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q


def enviar_alerta_admins(asunto, mensaje):
    """
    Envía correo a usuarios activos con rol admin/superadmin.
    Si falla el correo, no rompe el flujo principal del sistema.
    """
    destinatarios = list(
        User.objects.filter(
            is_active=True,
        ).filter(
            Q(is_superuser=True) | Q(is_staff=True)
        ).exclude(
            email=""
        ).values_list("email", flat=True).distinct()
    )

    if not destinatarios:
        return False

    try:
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios,
            fail_silently=True,
        )
        return True
    except Exception:
        return False


def notificar_stock_critico(producto, contexto="operación"):
    """
    Envía correo si el stock queda crítico (<= 5) o agotado (= 0).
    """
    if producto is None:
        return False
    if producto.stock > 5:
        return False

    if producto.stock == 0:
        nivel = "AGOTADO"
    else:
        nivel = "CRÍTICO"

    asunto = f"[Inventario] Stock {nivel}: {producto.nombre}"
    mensaje = (
        "Se detectó una alerta de inventario.\n\n"
        f"Producto: {producto.nombre}\n"
        f"Stock actual: {producto.stock}\n"
        f"Contexto: {contexto}\n\n"
        "Revisa el módulo de productos/compras para reabastecer."
    )
    return enviar_alerta_admins(asunto, mensaje)
