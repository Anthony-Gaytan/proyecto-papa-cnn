# Frontend - Deteccion de enfermedades en hojas de papa

Este frontend consume la API FastAPI creada en la Fase 2.
Permite seleccionar una imagen de hoja de papa, enviarla al endpoint `/predict` y visualizar la clase predicha, la confianza y las probabilidades por clase.

## Archivos

| Archivo | Responsabilidad |
|---|---|
| `index.html` | Estructura de la interfaz web. |
| `styles.css` | Estilos visuales y diseno responsive. |
| `app.js` | Logica de seleccion de imagen, vista previa, llamada al backend y renderizado de resultados. |
| `README.md` | Instrucciones de uso del frontend. |

## Requisito

Antes de usar el frontend, el backend debe estar activo:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.app:app --reload
```

La API debe estar disponible en:

```text
http://127.0.0.1:8000
```

## Uso abriendo el archivo

Puedes abrir directamente:

```text
frontend/index.html
```

## Uso con servidor local simple

Desde la raiz del proyecto:

```powershell
.\venv\Scripts\python.exe -m http.server 5500 -d frontend
```

Luego abre:

```text
http://127.0.0.1:5500
```

## Flujo

1. Selecciona una imagen `.jpg`, `.jpeg` o `.png`.
2. Revisa la vista previa.
3. Presiona `Analizar imagen`.
4. El frontend envia la imagen a `http://127.0.0.1:8000/predict`.
5. La respuesta muestra clase predicha, confianza, probabilidades y un mensaje interpretativo.
