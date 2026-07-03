from django.db import models
from django.contrib.auth.models import User


# Solo dos roles: superadmin (is_superuser=True) y admin (is_superuser=False)
ROLES = (
    ('admin',      'Administrador'),
)


class PerfilUsuario(models.Model):
    """
    Perfil extendido del usuario Django.
    - superadmin → is_superuser=True, acceso total.
    - admin      → is_superuser=False, acceso al sistema sin gestión de usuarios.
    El campo rol se sincroniza con is_superuser automáticamente en save().
    """
    user     = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol      = models.CharField(max_length=20, choices=ROLES, default='admin', verbose_name='Rol')
    cedula   = models.CharField(max_length=20, unique=True, verbose_name='Cédula')
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name='Teléfono')
    foto     = models.ImageField(upload_to='admins/', blank=True, null=True, verbose_name='Foto de perfil')

    def save(self, *args, **kwargs):
        # Sincroniza is_superuser con el rol elegido
        self.user.is_superuser = (self.rol == 'superadmin')
        self.user.is_staff     = (self.rol == 'superadmin')  # is_staff necesario para acceder al /admin/
        self.user.save(update_fields=['is_superuser', 'is_staff'])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"

    class Meta:
        verbose_name        = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
        db_table            = 'perfil_usuario'
