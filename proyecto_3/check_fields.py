#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
campos_faltantes = []

# Verificar precio_unitario
cursor.execute('''
    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME="compra" AND COLUMN_NAME="precio_unitario"
''')
if not cursor.fetchone():
    campos_faltantes.append('precio_unitario')
    cursor.execute('ALTER TABLE compra ADD COLUMN precio_unitario DECIMAL(10,2) DEFAULT 0')

# Verificar usuario_id
cursor.execute('''
    SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME="compra" AND COLUMN_NAME="usuario_id"
''')
if not cursor.fetchone():
    campos_faltantes.append('usuario_id')
    cursor.execute('ALTER TABLE compra ADD COLUMN usuario_id INT NULL')

if campos_faltantes:
    print(f'✓ Campos agregados: {campos_faltantes}')
else:
    print('✓ Todos los campos requeridos existen')

cursor.close()
