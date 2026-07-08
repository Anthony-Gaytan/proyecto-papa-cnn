from typing import Dict, List, Optional

from pydantic import BaseModel, Field, RootModel


class RootResponse(BaseModel):
    project: str
    status: str
    model: str
    version: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class ModelInfoResponse(BaseModel):
    model_name: str
    model_type: str
    number_of_classes: int
    class_names: List[str]
    image_size: List[int]
    accuracy: Optional[float]
    loaded_at: Optional[str]


class PredictResponse(BaseModel):
    predicted_class: str = Field(alias="class")
    confidence: float
    probabilities: Dict[str, float]

    model_config = {
        "populate_by_name": True,
    }


class ClassesResponse(RootModel[List[str]]):
    pass
