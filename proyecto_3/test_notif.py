#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.context_processors import notificaciones
from django.test import RequestFactory
from django.contrib.auth.models import User

factory = RequestFactory()
request = factory.get('/')
request.user = User.objects.filter(is_active=True).first()

try:
    result = notificaciones(request)
    print('Total notificaciones:', result.get('total_notificaciones'))
    notifs = result.get('notificaciones', [])
    print('Notificaciones:', len(notifs))
    for i, n in enumerate(notifs[:3]):
        print(f'{i+1}. {n.get("mensaje")[:60]}')
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()
