# Guia de despliegue

Este documento resume como preparar el repositorio y desplegar el proyecto con backend en Render y frontend en Netlify.

## Estrategia del modelo

No se usa Git LFS.

El modelo original:

```text
resultados/modelo_papa_cnn.h5
```

se conserva localmente, pero no se sube porque pesa mas de 100 MB.

Para despliegue se usa:

```text
resultados/modelo_papa_cnn.keras
```

Este archivo pesa aproximadamente 42.64 MB y puede subirse a GitHub normal.
El backend carga primero `.keras` y usa `.h5` como fallback si existe.

## Archivos que deben subirse

- `main.py`
- `backend/`
- `frontend/`
- `spark/`
- `docker/`
- `resultados/modelo_papa_cnn.keras`
- `resultados/metrics.json`
- `resultados/reporte_metricas.txt`
- graficas y matriz en `resultados/*.png`
- `.gitignore`
- `README.md`
- `README_DEPLOY.md`

## Archivos y carpetas que no deben subirse

- `venv/`
- `dataset/`
- `dataset_split/`
- `spark/output/`
- `__pycache__/`
- `resultados/modelo_papa_cnn.h5`
- `resultados/modelo_papa_cnn.tflite`
- `resultados/modelo_papa_cnn_quant.tflite`

## Subir a GitHub

Desde la raiz del proyecto:

```powershell
git init
git add .
git status --short
git commit -m "Preparar proyecto CNN papa para despliegue"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

Antes del commit verifica que no aparezcan:

```text
venv/
dataset/
dataset_split/
resultados/modelo_papa_cnn.h5
```

## Backend en Render

1. Crear un nuevo Web Service en Render.
2. Conectar el repositorio GitHub.
3. Elegir despliegue con Docker.
4. Usar como Dockerfile:

```text
docker/backend.Dockerfile
```

5. Configurar variables de entorno cuando se tenga la URL final de Netlify:

```text
CORS_ORIGINS=https://TU-SITIO.netlify.app,http://localhost:8080,http://127.0.0.1:8080
```

6. Verificar:

```text
https://TU-BACKEND.onrender.com/health
https://TU-BACKEND.onrender.com/docs
```

## Frontend en Netlify

1. Crear un nuevo sitio desde GitHub.
2. Seleccionar el repositorio.
3. Usar como carpeta publicada:

```text
frontend
```

4. Configurar la URL publica del backend en el frontend antes del despliegue final.

## Pendiente antes del despliegue web

Para produccion falta hacer configurable la URL del backend en `frontend/app.js` y ajustar CORS dinamico con `CORS_ORIGINS`.
Ese cambio debe hacerse cuando ya se conozcan las URLs publicas de Render y Netlify.
