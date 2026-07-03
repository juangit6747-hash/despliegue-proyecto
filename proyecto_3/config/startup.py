import os
import logging

from django.contrib.auth import get_user_model
from django.db import ProgrammingError, OperationalError

logger = logging.getLogger(__name__)


def create_default_superuser():
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not username or not email or not password:
        return

    User = get_user_model()

    try:
        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            if existing_user.is_superuser:
                return

            existing_user.is_superuser = True
            existing_user.is_staff = True
            existing_user.set_password(password)
            existing_user.save(update_fields=['is_superuser', 'is_staff', 'password'])
            logger.info('Updated existing user %s to superuser.', username)
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        logger.info('Created default superuser %s from environment.', username)

    except (ProgrammingError, OperationalError) as exc:
        # This can occur before migrations have run or when the database is not yet ready.
        logger.warning('Could not create default superuser yet: %s', exc)
    except Exception as exc:
        logger.exception('Failed to create default superuser: %s', exc)
