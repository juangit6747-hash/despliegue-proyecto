"""
VISTAS PARA RESPALDO Y RESTAURACION DE BD
Funciona dentro de Docker — usa el contenedor MySQL (host=db)
"""
import os
import subprocess
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from app.decorators import superadmin_required
import shutil


def obtener_credenciales_mysql():
    db_config = settings.DATABASES['default']
    return {
        'host':     db_config.get('HOST', 'db'),
        'user':     db_config.get('USER', 'root'),
        'password': db_config.get('PASSWORD', ''),
        'database': db_config.get('NAME', 'proyecto'),
        'port':     str(db_config.get('PORT', 3306)),
    }


def obtener_bin(nombre):
    """En Docker (Linux) busca el binario en el PATH."""
    return shutil.which(nombre) or nombre


def _env_mysql(creds):
    env = os.environ.copy()
    env['MYSQL_PWD'] = creds['password']
    return env


def probar_conexion_mysql():
    creds = obtener_credenciales_mysql()
    try:
        cmd = [
            obtener_bin('mysql'),
            '-h', creds['host'],
            '-u', creds['user'],
            '-P', creds['port'],
            '-e', 'SELECT 1;',
            creds['database'],
        ]
        resultado = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10,
            env=_env_mysql(creds),
        )
        return resultado.returncode == 0
    except Exception:
        return False


@superadmin_required
@require_http_methods(["GET", "POST"])
def backup(request):
    if request.method == "POST":
        accion = request.POST.get('accion')
        try:
            if accion == 'backup_completo':
                if not probar_conexion_mysql():
                    return JsonResponse(
                        {'error': 'No se puede conectar a MySQL.'},
                        status=400
                    )
                return realizar_respaldo_completo()
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    mysql_ok = probar_conexion_mysql()
    return render(request, 'backup/menu.html', {
        'titulo': 'Respaldo y Restauración de Base de Datos',
        'mysql_conectado': mysql_ok,
    })


@superadmin_required
@require_http_methods(["GET", "POST"])
def restaurar_datos(request):
    if 'archivo' not in request.FILES:
        return JsonResponse({'error': 'No se proporcionó archivo.'}, status=400)
    archivo = request.FILES['archivo']
    try:
        if not archivo.name.endswith('.sql'):
            return JsonResponse({'error': 'El archivo debe tener extensión .sql'}, status=400)
        contenido_sql = archivo.read().decode('utf-8')
        restaurar_bd_desde_sql(contenido_sql)
        return JsonResponse({'exito': True, 'mensaje': 'Base de datos restaurada correctamente.'})
    except Exception as e:
        return JsonResponse({'error': f'Error al restaurar: {str(e)}'}, status=400)


def realizar_respaldo_completo():
    creds = obtener_credenciales_mysql()
    try:
        cmd = [
            obtener_bin('mysqldump'),
            '-h', creds['host'],
            '-u', creds['user'],
            '-P', creds['port'],
            creds['database'],
        ]
        resultado = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60,
            env=_env_mysql(creds),
        )
        if resultado.returncode != 0:
            raise Exception(f"Error mysqldump: {resultado.stderr}")
        sql_content = resultado.stdout
        if not sql_content.strip():
            raise Exception("El respaldo está vacío.")
        sql_content = (
            f"-- Respaldo de {creds['database']}\n"
            f"-- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            + sql_content
        )
        return generar_archivo_descarga(sql_content, 'backup_completo')
    except subprocess.TimeoutExpired:
        raise Exception("Timeout al ejecutar mysqldump.")
    except Exception as e:
        raise Exception(f"Error en respaldo: {str(e)}")


def restaurar_bd_desde_sql(contenido_sql):
    creds = obtener_credenciales_mysql()
    try:
        cmd = [
            obtener_bin('mysql'),
            '-h', creds['host'],
            '-u', creds['user'],
            '-P', creds['port'],
            creds['database'],
        ]
        proceso = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, env=_env_mysql(creds),
        )
        stdout, stderr = proceso.communicate(input=contenido_sql, timeout=120)
        if proceso.returncode != 0:
            raise Exception(f"Error MySQL: {stderr}")
        return True
    except subprocess.TimeoutExpired:
        raise Exception("Timeout al restaurar.")
    except Exception as e:
        raise Exception(f"Error al restaurar: {str(e)}")


def generar_archivo_descarga(contenido_sql, nombre_archivo):
    response = HttpResponse(contenido_sql.encode('utf-8'), content_type='application/sql')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}_{timestamp}.sql"'
    return response
