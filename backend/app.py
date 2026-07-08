from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .model_loader import load_model_once
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carga el modelo una sola vez cuando inicia FastAPI.
    load_model_once()
    yield


app = FastAPI(
    title="API CNN Papa",
    description="Servicio REST para detectar enfermedades en hojas de papa.",
    version="1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://proyecto-papa-cnn.netlify.app",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
