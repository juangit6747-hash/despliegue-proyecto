import re
from django import forms
from django.contrib.auth.models import User
from .models import PerfilUsuario, ROLES


# ── Helpers de validación ────────────────────────────────────────────────────

def _solo_letras(valor, campo='El campo'):
    """Acepta letras (incluye tildes y ñ) y espacios. Sin números ni especiales."""
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$', valor):
        raise forms.ValidationError(f'{campo} solo puede contener letras y espacios.')

def _validar_password(password):
    """Mínimo 8 caracteres, una mayúscula y un número."""
    if len(password) < 8:
        raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
    if not re.search(r'[A-Z]', password):
        raise forms.ValidationError('La contraseña debe contener al menos una letra mayúscula.')
    if not re.search(r'[0-9]', password):
        raise forms.ValidationError('La contraseña debe contener al menos un número.')


# ── Formulario CREAR usuario ─────────────────────────────────────────────────

class AdminCrearForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':        'form-control',
            'placeholder':  'Mín. 8 caracteres, una mayúscula y un número',
            'autocomplete': 'new-password',
            'id':           'id_password',
        }),
        label='Contraseña'
    )
    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':        'form-control',
            'placeholder':  'Repite la contraseña',
            'autocomplete': 'new-password',
            'id':           'id_confirmar_password',
        }),
        label='Confirmar contraseña'
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username':   'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name':  'Apellido',
            'email':      'Correo electrónico',
        }
        widgets = {
            'username':   forms.TextInput(attrs={
                'class': 'form-control', 'autocomplete': 'off',
                'placeholder': 'Solo letras, números y guión bajo',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nombre(s)',
            }),
            'last_name':  forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Apellido(s)',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'correo@ejemplo.com',
            }),
        }

    # ── Validaciones campo a campo ──

    def clean_first_name(self):
        valor = self.cleaned_data.get('first_name', '').strip()
        if not valor:
            raise forms.ValidationError('El nombre es obligatorio.')
        if len(valor) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        _solo_letras(valor, 'El nombre')
        return valor

    def clean_last_name(self):
        valor = self.cleaned_data.get('last_name', '').strip()
        if not valor:
            raise forms.ValidationError('El apellido es obligatorio.')
        if len(valor) < 2:
            raise forms.ValidationError('El apellido debe tener al menos 2 caracteres.')
        _solo_letras(valor, 'El apellido')
        return valor

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError('El nombre de usuario es obligatorio.')
        if len(username) < 3:
            raise forms.ValidationError('El usuario debe tener al menos 3 caracteres.')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError('El usuario solo puede contener letras, números y guión bajo (_).')
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError('El correo electrónico es obligatorio.')
        qs = User.objects.filter(email=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        _validar_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirmar_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirmar_password', 'Las contraseñas no coinciden.')
        return cleaned_data


# ── Formulario EDITAR usuario ────────────────────────────────────────────────

class AdminEditarForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':        'form-control',
            'placeholder':  'Dejar en blanco para no cambiar',
            'autocomplete': 'new-password',
            'id':           'id_password_edit',
        }),
        label='Nueva contraseña',
        required=False
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username':   'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name':  'Apellido',
            'email':      'Correo electrónico',
        }
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_first_name(self):
        valor = self.cleaned_data.get('first_name', '').strip()
        if not valor:
            raise forms.ValidationError('El nombre es obligatorio.')
        if len(valor) < 2:
            raise forms.ValidationError('El nombre debe tener al menos 2 caracteres.')
        _solo_letras(valor, 'El nombre')
        return valor

    def clean_last_name(self):
        valor = self.cleaned_data.get('last_name', '').strip()
        if not valor:
            raise forms.ValidationError('El apellido es obligatorio.')
        if len(valor) < 2:
            raise forms.ValidationError('El apellido debe tener al menos 2 caracteres.')
        _solo_letras(valor, 'El apellido')
        return valor

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError('El nombre de usuario es obligatorio.')
        if len(username) < 3:
            raise forms.ValidationError('El usuario debe tener al menos 3 caracteres.')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError('El usuario solo puede contener letras, números y guión bajo (_).')
        qs = User.objects.filter(username=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError('El correo electrónico es obligatorio.')
        qs = User.objects.filter(email=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if password:  # solo valida si escribieron algo
            _validar_password(password)
        return password


# ── Formulario PERFIL ────────────────────────────────────────────────────────

class PerfilForm(forms.ModelForm):
    class Meta:
        model  = PerfilUsuario
        fields = ['rol', 'cedula', 'telefono', 'foto']
        labels = {
            'rol':      'Rol',
            'cedula':   'Cédula',
            'telefono': 'Teléfono',
            'foto':     'Foto de perfil',
        }
        widgets = {
            'rol':      forms.Select(attrs={'class': 'form-control'}),
            'cedula':   forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Solo números',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: 3001234567',
            }),
            'foto':     forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png', 
            }),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula', '').strip()
        if not cedula:
            raise forms.ValidationError('La cédula es obligatoria.')
        if not re.match(r'^\d+$', cedula):
            raise forms.ValidationError('La cédula solo puede contener números.')
        if len(cedula) < 6 or len(cedula) > 12:
            raise forms.ValidationError('La cédula debe tener entre 6 y 12 dígitos.')
        qs = PerfilUsuario.objects.filter(cedula=cedula)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Esta cédula ya está registrada.')
        return cedula

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono:  # opcional
            if not re.match(r'^\d+$', telefono):
                raise forms.ValidationError('El teléfono solo puede contener números.')
            if len(telefono) < 7 or len(telefono) > 15:
                raise forms.ValidationError('El teléfono debe tener entre 7 y 15 dígitos.')
        return telefono

    def clean_foto(self):
        import imghdr
        foto = self.cleaned_data.get('foto')
        if foto and hasattr(foto, 'size'):
            if foto.size > 2 * 1024 * 1024:  # 2 MB
                raise forms.ValidationError('La imagen no puede superar 2 MB.')
            # Verificar content-type declarado
            tipo = getattr(foto, 'content_type', '')
            if tipo and not tipo.startswith('image/'):
                raise forms.ValidationError('El archivo debe ser una imagen válida (JPG, PNG o GIF).')
            # Verificar magic bytes reales del archivo (evita renombrar .txt a .png)
            foto.seek(0)
            cabecera = foto.read(12)
            foto.seek(0)
            tipo_real = imghdr.what(None, h=cabecera)
            if tipo_real not in ('jpeg', 'png'):
                raise forms.ValidationError(
                    'El archivo no es una imagen válida. No se aceptan archivos de texto u otros formatos renombrados como imagen.'
                )
        return foto