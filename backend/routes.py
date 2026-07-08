from fastapi import APIRouter, File, UploadFile

from .model_loader import get_model_info, is_model_loaded
from .predict import predict_image
from .schemas import (
    ClassesResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictResponse,
    RootResponse,
)


router = APIRouter()

CLASS_NAMES = [
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
]


@router.get("/", response_model=RootResponse)
def root():
    # Endpoint base para verificar que la API esta disponible.
    return {
        "project": "Detección de enfermedades en hojas de papa",
        "status": "running",
        "model": "CNN",
        "version": "1.0",
    }


@router.get("/health", response_model=HealthResponse)
def health():
    # Informa si el servicio esta activo y si el modelo fue cargado.
    return {
        "status": "healthy",
        "model_loaded": is_model_loaded(),
    }


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    # Devuelve metadata del modelo y metricas guardadas durante la Fase 1.
    return get_model_info()


@router.get("/classes", response_model=ClassesResponse)
def classes():
    # Lista las clases que la CNN puede predecir.
    return CLASS_NAMES


@router.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile = File(...)):
    # Delega validacion, preprocesamiento e inferencia al modulo predict.
    return await predict_image(file)
