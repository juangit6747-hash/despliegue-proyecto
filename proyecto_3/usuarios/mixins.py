from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy


class SuperadminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Solo permite acceso a superadmins (is_superuser=True).
    Usar en todas las vistas de gestión de usuarios.
    """
    login_url       = reverse_lazy('login')   # nombre correcto del proyecto
    raise_exception = True

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied('No tienes permiso para acceder a esta sección.')
