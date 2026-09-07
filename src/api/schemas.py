"""Pydantic schemas for the AOI REST API."""

from pydantic import BaseModel, Field

from src.core.grader import DefectType, InspectionGrade


class BoundingBox(BaseModel):
    x_min: float = Field(
        ..., description="Normalized top-left X coordinate [0.0 - 1.0]"
    )
    y_min: float = Field(
        ..., description="Normalized top-left Y coordinate [0.0 - 1.0]"
    )
    x_max: float = Field(
        ..., description="Normalized bottom-right X coordinate [0.0 - 1.0]"
    )
    y_max: float = Field(
        ..., description="Normalized bottom-right Y coordinate [0.0 - 1.0]"
    )


class PolygonPoint(BaseModel):
    x: float = Field(..., description="Normalized X coordinate [0.0 - 1.0]")
    y: float = Field(..., description="Normalized Y coordinate [0.0 - 1.0]")


class DetectedDefect(BaseModel):
    defect_id: int
    defect_type: DefectType
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: BoundingBox
    polygon: list[PolygonPoint]
    pixel_area: int = Field(..., description="Defect mask pixel count")


class DetectedFruit(BaseModel):
    fruit_id: int
    fruit_type: str = Field(default="fruit")
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: BoundingBox
    polygon: list[PolygonPoint]
    pixel_area: int = Field(..., description="Fruit mask pixel count")


class InspectionTiming(BaseModel):
    preprocess_ms: float
    inference_ms: float
    postprocess_ms: float
    grading_ms: float
    total_ms: float


class InspectionResponse(BaseModel):
    inspection_id: str
    timestamp: str
    image_width: int
    image_height: int
    fruit: DetectedFruit | None = None
    defects: list[DetectedDefect] = Field(default_factory=list)
    defect_ratio_percent: float = Field(..., ge=0.0, le=100.0)
    grade: InspectionGrade
    reject_reason: str | None = None
    timing: InspectionTiming
    overlay_image_base64: str | None = None


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    execution_provider: str
    version: str
