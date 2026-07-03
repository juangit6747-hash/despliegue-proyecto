import random
import time

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail

from app.decorators import admin_login_required


User = get_user_model()


class LoginView(View):
    template_name = 'Login/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('inicio')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
                return redirect('inicio')
            else:
                messages.error(request, 'Tu cuenta está desactivada. Contacta al administrador.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

        return render(request, self.template_name)


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Sesión cerrada correctamente.')
        return redirect('login')

    def post(self, request):
        return self.get(request)


def send_recovery_code(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)

    email = request.POST.get('email', '').strip()
    if not email:
        return JsonResponse({'ok': False, 'error': 'Ingresa tu correo.'})

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return JsonResponse({'ok': False, 'error': 'No existe una cuenta asociada a ese correo.'})

    codigo = f'{random.randint(100000, 999999)}'
    request.session['recover_email'] = email.lower()
    request.session['recover_code'] = codigo
    request.session['recover_code_created'] = int(time.time())
    request.session['recover_code_validated'] = False
    request.session.modified = True

    asunto = 'Código de recuperación'
    mensaje = (
        f'Hola {user.get_full_name() or user.username},\n\n'
        f'Tu código de recuperación es: {codigo}\n\n'
        'Si no solicitaste este código, ignora este mensaje.'
    )

    try:
        send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': 'No se pudo enviar el correo. Revisa la configuración.'})

    return JsonResponse({'ok': True})


def validate_recovery_code(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)

    email = request.POST.get('email', '').strip().lower()
    codigo = request.POST.get('code', '').strip()
    if not email or not codigo:
        return JsonResponse({'ok': False, 'error': 'Correo y código son obligatorios.'})

    session_email = request.session.get('recover_email')
    session_code = request.session.get('recover_code')
    created = request.session.get('recover_code_created')
    if not session_email or not session_code or not created:
        return JsonResponse({'ok': False, 'error': 'No hay un código enviado para este correo.'})
    if email != session_email:
        return JsonResponse({'ok': False, 'error': 'El correo no coincide con el código enviado.'})
    if int(time.time()) - int(created) > 600:
        return JsonResponse({'ok': False, 'error': 'El código ha expirado. Solicita uno nuevo.'})
    if codigo != session_code:
        return JsonResponse({'ok': False, 'error': 'Código incorrecto.'})

    request.session['recover_code_validated'] = True
    request.session.modified = True

    return JsonResponse({'ok': True})


def reset_password(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)

    email = request.session.get('recover_email')
    validated = request.session.get('recover_code_validated')
    if not email or not validated:
        return JsonResponse({'ok': False, 'error': 'Primero valida el código recibido.'})

    password = request.POST.get('password', '').strip()
    confirm_password = request.POST.get('confirm_password', '').strip()
    if not password or not confirm_password:
        return JsonResponse({'ok': False, 'error': 'Completa ambos campos de contraseña.'})
    if password != confirm_password:
        return JsonResponse({'ok': False, 'error': 'Las contraseñas no coinciden.'})
    if len(password) < 8:
        return JsonResponse({'ok': False, 'error': 'La contraseña debe tener al menos 8 caracteres.'})

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return JsonResponse({'ok': False, 'error': 'No se encontró la cuenta para restablecer la contraseña.'})

    user.set_password(password)
    user.save()

    request.session.pop('recover_email', None)
    request.session.pop('recover_code', None)
    request.session.pop('recover_code_created', None)
    request.session.pop('recover_code_validated', None)
    request.session.modified = True

    return JsonResponse({'ok': True})


login_view  = LoginView.as_view()
logout_view = LogoutView.as_view()
