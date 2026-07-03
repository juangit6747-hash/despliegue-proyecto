import os
import sys

import django
from django.contrib.auth import get_user_model
from django.core.management import call_command


def create_super_admin():
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

    if not username or not password or not email:
        print('No superuser environment variables found, skipping creation.')
        return

    User = get_user_model()
    user = User.objects.filter(username=username).first()

    if user:
        if user.is_superuser:
            print(f'Superuser {username} already exists. Updating password and email.')
        else:
            print(f'User {username} exists, updating to superuser.')

        user.email = email
        user.is_superuser = True
        user.is_staff = True
        user.set_password(password)
        user.save(update_fields=['email', 'is_superuser', 'is_staff', 'password'])
        print(f'Updated user {username} as superuser.')
        return

    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Created superuser {username}.')


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

    print('Applying migrations...')
    call_command('migrate', '--noinput')

    create_super_admin()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('Error during create_super_admin execution:', exc)
        sys.exit(1)
