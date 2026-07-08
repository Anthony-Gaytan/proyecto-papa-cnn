import json
from datetime import datetime
from pathlib import Path
from typing import Any

import tensorflow as tf
from fastapi import HTTPException


BASE_DIR = Path(__file__).resolve().parent.parent
KERAS_MODEL_PATH = BASE_DIR / "resultados" / "modelo_papa_cnn.keras"
H5_MODEL_PATH = BASE_DIR / "resultados" / "modelo_papa_cnn.h5"
METRICS_PATH = BASE_DIR / "resultados" / "metrics.json"

CLASS_NAMES = [
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
]
IMAGE_SIZE = [224, 224]

_model = None
_loaded_at = None
_metrics: dict[str, Any] = {}
_model_path = None


def load_metrics():
    # Lee las metricas de Fase 1 si el archivo existe.
    if not METRICS_PATH.exists():
        return {}

    with open(METRICS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def load_model_once():
    # Carga el modelo en memoria una sola vez durante el ciclo de vida de FastAPI.
    global _model, _loaded_at, _metrics, _model_path

    if _model is not None:
        return _model

    if KERAS_MODEL_PATH.exists():
        selected_model_path = KERAS_MODEL_PATH
    elif H5_MODEL_PATH.exists():
        selected_model_path = H5_MODEL_PATH
    else:
        raise FileNotFoundError(
            "No se encontro el modelo en resultados/modelo_papa_cnn.keras "
            "ni en resultados/modelo_papa_cnn.h5"
        )

    _model = tf.keras.models.load_model(selected_model_path, compile=False)
    _model_path = selected_model_path
    _loaded_at = datetime.now().isoformat(timespec="seconds")
    _metrics = load_metrics()
    return _model


def get_model():
    # Devuelve el modelo ya cargado; si no existe, intenta cargarlo.
    if _model is None:
        load_model_once()

    if _model is None:
        raise HTTPException(status_code=503, detail="El modelo no esta cargado.")

    return _model


def is_model_loaded():
    return _model is not None


def get_model_info():
    # Combina metadata fija del modelo con metricas generadas por el entrenamiento.
    metrics = _metrics or load_metrics()
    accuracy = metrics.get("test_accuracy")

    return {
        "model_name": _model_path.name if _model_path else KERAS_MODEL_PATH.name,
        "model_type": "CNN",
        "number_of_classes": len(CLASS_NAMES),
        "class_names": CLASS_NAMES,
        "image_size": metrics.get("img_size", IMAGE_SIZE),
        "accuracy": accuracy,
        "loaded_at": _loaded_at,
    }
