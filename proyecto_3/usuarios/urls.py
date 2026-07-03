from django.urls import path
from .views import (
    ListarUsuariosView,
    CrearUsuarioView,
    EditarUsuarioView,
    CambiarEstadoUsuarioView,
)

app_name = 'usuarios'

urlpatterns = [
    path('listar/',          ListarUsuariosView.as_view(),      name='listar'),
    path('crear/',           CrearUsuarioView.as_view(),         name='crear'),
    path('editar/<int:pk>/', EditarUsuarioView.as_view(),        name='editar'),
    path('estado/<int:pk>/', CambiarEstadoUsuarioView.as_view(), name='cambiar_estado'),
]
