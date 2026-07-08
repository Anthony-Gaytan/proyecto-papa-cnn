# Despliegue Docker

Esta fase contieneiza el backend FastAPI y el frontend web del proyecto.
No modifica el entrenamiento, el modelo, el dataset, Spark ni los resultados.

## Arquitectura

| Servicio | Imagen base | Funcion |
|---|---|---|
| `backend` | `python:3.11-slim` | Ejecuta FastAPI con Uvicorn y consume el modelo CNN. |
| `frontend` | `nginx:1.27-alpine` | Sirve la interfaz HTML/CSS/JS. |

El backend monta la carpeta `resultados/` como volumen de solo lectura:

```text
../resultados:/app/resultados:ro
```

Esto permite usar:

```text
resultados/modelo_papa_cnn.h5
resultados/metrics.json
```

sin copiar ni modificar los artefactos entrenados.

## Puertos

| Servicio | Puerto host | Puerto contenedor |
|---|---:|---:|
| Backend FastAPI | `8000` | `8000` |
| Frontend Nginx | `8080` | `80` |

## Construir

Desde la carpeta raiz del proyecto:

```powershell
docker compose -f docker/docker-compose.yml build
```

## Levantar

Desde la carpeta raiz del proyecto:

```powershell
docker compose -f docker/docker-compose.yml up --build
```

## Levantar en segundo plano

```powershell
docker compose -f docker/docker-compose.yml up --build -d
```

## Detener

```powershell
docker compose -f docker/docker-compose.yml down
```

## Probar

Frontend:

```text
http://127.0.0.1:8080
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Health check:

```powershell
curl.exe http://127.0.0.1:8000/health
```

Prediccion:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/predict" -F "file=@dataset_split/test/Potato___Early_blight/0267d4ca-522e-4ca0-b1a2-ce925e5b54a2___RS_Early.B 7020.JPG"
```

## Red

`docker-compose.yml` crea una red bridge llamada `papa-cnn-network`.
Ambos servicios quedan conectados a esa red.
El navegador accede al backend mediante el puerto publicado `8000`.

## Nota

El frontend actual llama a:

```text
http://127.0.0.1:8000/predict
```

Por eso el backend se publica en el puerto `8000` del host.
