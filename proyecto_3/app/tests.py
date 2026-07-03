from django.test import TestCase
from app.models import Cliente


class PruebaBasica(TestCase):
    def test_verificar_entorno(self):
        "Prueba simple para validar que el CI/CD funciona"
        self.assertEqual(1 + 1, 2)

    def test_crear_cliente(self):
        "Prueba basica de creacion en base de datos"
        cliente = Cliente.objects.create(
            nombre='Cliente Prueba',
            telefono='3000000000',
            email='prueba@test.com',
        )
        consulta = Cliente.objects.filter(nombre='Cliente Prueba')
        self.assertTrue(consulta.exists())