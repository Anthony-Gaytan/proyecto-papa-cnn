# Backend FastAPI - CNN Papa

Este backend expone una API REST para consumir el modelo entrenado en la Fase 1.
No entrena la CNN, no modifica el dataset y no modifica `dataset_split`.
Solo carga el archivo `resultados/modelo_papa_cnn.h5` para realizar inferencia.

## Archivos

| Archivo | Por que existe |
|---|---|
| `app.py` | Crea la aplicacion FastAPI, configura metadata y carga el modelo una sola vez al iniciar. |
| `routes.py` | Define los endpoints REST de la API. |
| `predict.py` | Valida archivos, procesa imagenes y ejecuta la prediccion. |
| `model_loader.py` | Centraliza la carga del modelo y la lectura de `metrics.json`. |
| `schemas.py` | Define respuestas Pydantic para documentar la API. |
| `requirements.txt` | Lista las dependencias necesarias del backend. |
| `README.md` | Explica como instalar, ejecutar y probar el servicio. |

## Requisitos

El modelo debe existir en:

```text
resultados/modelo_papa_cnn.h5
```

Si existe `resultados/metrics.json`, el endpoint `/model-info` usara su informacion.

## Instalacion

Desde la carpeta raiz del proyecto:

```powershell
.\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

## Ejecucion

Desde la carpeta raiz del proyecto:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.app:app --reload
```

La API quedara disponible en:

```text
http://127.0.0.1:8000
```

La documentacion automatica estara en:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### GET /

Devuelve el estado basico del proyecto.

### GET /health

Indica si el servicio esta activo y si el modelo fue cargado.

### GET /model-info

Devuelve nombre del modelo, tipo, clases, tamano esperado de imagen, accuracy y fecha de carga.

### GET /classes

Devuelve la lista de clases que reconoce el modelo.

### POST /predict

Recibe una imagen `.jpg`, `.jpeg` o `.png` usando `multipart/form-data`.
Valida extension, tipo de archivo, tamano maximo, archivo vacio e imagen corrupta.

Ejemplo con PowerShell:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/predict" -F "file=@dataset_split/test/Potato___Late_blight/imagen.jpg"
```
