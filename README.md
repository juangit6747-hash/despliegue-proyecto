# proyecto_grupo_3

## Cómo ejecutar el proyecto

Este proyecto puede correr de dos formas:

1. Con Docker Compose
   - Ejecuta `docker compose up --build`
   - Dentro del contenedor web, la base de datos se resuelve como `db`.
   - El contenedor MySQL usa el puerto `3306` internamente.

2. Directamente en Windows
   - Ejecuta `python manage.py runserver` desde la carpeta `proyecto_3`.
   - Usa `DB_HOST=127.0.0.1` y `DB_PORT=3307` si te conectas al contenedor MySQL desde el host.

> El error `Unknown server host 'db'` ocurre cuando Django se ejecuta en Windows y `DB_HOST=db` está configurado, porque el host `db` solo existe dentro de la red de Docker.