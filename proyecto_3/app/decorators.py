from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_login_required(view_func):
    """
    Reemplaza la sesion manual por Django auth.
    Permite acceso a cualquier usuario autenticado (admin o superadmin).
    Los 12 archivos que usan este decorador no necesitan cambios.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_active:
            messages.error(request, 'Tu cuenta está desactivada. Contacta al administrador.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def superadmin_required(view_func):
    """
    Solo permite acceso a superadmins (is_superuser=True).
    Usar en vistas de gestión de usuarios y backup.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('inicio')
        return view_func(request, *args, **kwargs)
    return wrapper