from django.test import TestCase
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario


class PruebaBasica(TestCase):
    def test_verificar_entorno(self):
        "Prueba simple para validar que el CI/CD funciona"
        self.assertEqual(1 + 1, 2)

    def test_crear_perfil_usuario(self):
        "Prueba basica de creacion de perfil ligado a un usuario"
        user = User.objects.create_user(username='pruebauser', password='clave12345')
        perfil = PerfilUsuario.objects.create(
            user=user,
            rol='admin',
            cedula='1000000000',
        )
        consulta = PerfilUsuario.objects.filter(cedula='1000000000')
        self.assertTrue(consulta.exists())
        self.assertEqual(perfil.user.username, 'pruebauser')