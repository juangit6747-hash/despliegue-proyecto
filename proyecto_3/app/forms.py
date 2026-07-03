from django import forms
from django.core.exceptions import ValidationError
import re


class ventaForm(forms.Form):
    cliente = forms.CharField(max_length=100)
    estado  = forms.ChoiceField(choices=[
        ('Completada', 'Completada'),
        ('Pendiente',  'Pendiente'),
    ])

    def clean_cliente(self):
        cliente = self.cleaned_data.get('cliente', '').strip()
        if not cliente:
            raise ValidationError('Por favor ingrese un nombre de cliente.')
        if re.search(r'\d', cliente):
            raise ValidationError('El nombre del cliente no puede contener números.')
        if len(cliente) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        return cliente