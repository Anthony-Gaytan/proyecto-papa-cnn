# Deteccion de enfermedades en hojas de papa con CNN

Proyecto de percepcion computacional para clasificar hojas de papa en tres clases:

- `Potato___Early_blight`
- `Potato___Late_blight`
- `Potato___healthy`

El proyecto incluye entrenamiento CNN, backend FastAPI, frontend web, pipeline batch PySpark y configuracion Docker.

## Estructura

| Ruta | Descripcion |
|---|---|
| `main.py` | Entrenamiento CNN corregido con split train/validation/test, class weight y metricas sobre test. |
| `backend/` | API REST FastAPI para cargar el modelo y realizar predicciones. |
| `frontend/` | Interfaz HTML/CSS/JS para subir imagenes y ver resultados. |
| `spark/` | Pipeline batch PySpark para analizar metadata de `dataset_split/`. |
| `docker/` | Dockerfiles y Docker Compose para despliegue local. |
| `resultados/` | Modelo desplegable, metricas y evidencias del entrenamiento. |

## Modelo usado para despliegue

El modelo original `resultados/modelo_papa_cnn.h5` pesa aproximadamente 128 MB y no se sube al repositorio.

Para despliegue gratuito se usa:

```text
resultados/modelo_papa_cnn.keras
```

Este archivo pesa aproximadamente 42.64 MB, puede subirse a GitHub normal y mantiene compatibilidad con:

```python
tf.keras.models.load_model()
```

El backend intenta cargar primero `modelo_papa_cnn.keras` y, si no existe, usa como fallback `modelo_papa_cnn.h5`.

## Resultados principales

Metricas sobre test despues de corregir el pipeline de entrenamiento:

| Metrica | Valor |
|---|---:|
| Accuracy test | `0.9506` |
| Loss test | `0.1241` |

## Ejecucion local del backend

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.app:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Ejecucion local del frontend

Abriendo directamente:

```text
frontend/index.html
```

O con servidor local:

```powershell
.\venv\Scripts\python.exe -m http.server 5500 -d frontend
```

## Ejecucion con Docker

```powershell
docker compose -f docker/docker-compose.yml up --build
```

Frontend:

```text
http://127.0.0.1:8080
```

Backend:

```text
http://127.0.0.1:8000
```

## Spark

```powershell
.\venv\Scripts\python.exe spark\spark_batch.py --partitions 4
```

## Carpetas excluidas del repositorio

No se suben:

- `venv/`
- `dataset/`
- `dataset_split/`
- `spark/output/`
- `__pycache__/`
- `resultados/modelo_papa_cnn.h5`

El dataset original debe mantenerse localmente o descargarse aparte.
