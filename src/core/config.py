"""Application configuration settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for Food Defect AOI pipeline."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Food Defect AOI System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Project root anchor
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Image constraints
    INPUT_IMAGE_SIZE: int = 640
    MAX_IMAGE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

    # Model paths (NVIDIA GPU Trained YOLOv8s-seg)
    MODEL_WEIGHTS_DIR: Path = Path(__file__).resolve().parent.parent.parent / "models" / "weights"
    MODEL_ONNX_DIR: Path = Path(__file__).resolve().parent.parent.parent / "models" / "onnx"
    DEFAULT_ONNX_MODEL: Path = Path(__file__).resolve().parent.parent.parent / "models" / "onnx" / "best_s.onnx"
    QUANTIZED_ONNX_MODEL: Path = Path(__file__).resolve().parent.parent.parent / "models" / "onnx" / "best_s_int8.onnx"
    MODEL_WEIGHTS_PATH: Path = Path(__file__).resolve().parent.parent.parent / "models" / "weights" / "best_s.pt"

    # Data paths
    DATA_DIR: Path = Path(__file__).resolve().parent.parent.parent / "data"
    SAMPLES_DIR: Path = Path(__file__).resolve().parent.parent.parent / "data" / "samples"
    FRONTEND_DIST: Path = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

    # Inspection tolerances
    GRADE_A_THRESHOLD_PERCENT: float = 1.0
    GRADE_B_THRESHOLD_PERCENT: float = 5.0
    CONFIDENCE_THRESHOLD: float = 0.35
    IOU_THRESHOLD: float = 0.45
    MIN_DEFECT_AREA_PIXELS: int = 50
    ENABLE_SPATIAL_INTERSECTION_FILTER: bool = True


settings = Settings()
