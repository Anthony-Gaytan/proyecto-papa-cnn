from io import BytesIO
from pathlib import Path

import numpy as np
from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from .model_loader import get_model


CLASS_NAMES = [
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
]

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
IMAGE_SIZE = (224, 224)


def validate_file_metadata(file: UploadFile):
    # Valida nombre, extension y tipo MIME antes de leer el contenido.
    if not file.filename:
        raise HTTPException(status_code=400, detail="El archivo no tiene nombre.")

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Extension no permitida. Use .jpg, .jpeg o .png.",
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no permitido. Use imagen JPEG o PNG.",
        )


async def read_and_validate_file(file: UploadFile):
    # Lee el archivo completo y valida que no este vacio ni exceda el limite.
    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="El archivo esta vacio.")

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="El archivo supera el tamano maximo permitido de 5 MB.",
        )

    return content


def preprocess_image(content: bytes):
    # Abre la imagen, valida que no este corrupta y aplica el mismo preprocesamiento usado por la CNN.
    try:
        image = Image.open(BytesIO(content))
        image.verify()
        image = Image.open(BytesIO(content)).convert("RGB")
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="La imagen esta corrupta o no es valida.") from exc
    except OSError as exc:
        raise HTTPException(status_code=400, detail="La imagen no pudo ser procesada.") from exc

    image = image.resize(IMAGE_SIZE)
    image_array = np.asarray(image, dtype=np.float32) / 255.0
    return np.expand_dims(image_array, axis=0)


async def predict_image(file: UploadFile):
    # Ejecuta el flujo completo de validacion, preprocesamiento e inferencia.
    validate_file_metadata(file)
    content = await read_and_validate_file(file)
    image_batch = preprocess_image(content)

    model = get_model()
    prediction = model.predict(image_batch, verbose=0)[0]

    predicted_index = int(np.argmax(prediction))
    predicted_class = CLASS_NAMES[predicted_index]
    confidence = float(prediction[predicted_index])
    probabilities = {
        class_name: float(probability)
        for class_name, probability in zip(CLASS_NAMES, prediction)
    }

    return {
        "class": predicted_class,
        "confidence": confidence,
        "probabilities": probabilities,
    }
