# Data Models & Schemas

This document defines the standard data structures, API payloads, and persistence schemas used across the entire Food Defect AOI system.

---

## 1. Domain Entities & Enums

```python
from enum import Enum

class DefectType(str, Enum):
    ROT = "rot"
    BRUISE = "bruise"
    SCAB = "scab"
    SCRATCH = "scratch"

class InspectionGrade(str, Enum):
    GRADE_A = "PASS_GRADE_A"
    GRADE_B = "PASS_GRADE_B"
    REJECT = "REJECT"
    NO_OBJECT = "NO_OBJECT"
```

---

## 2. API Request & Response Schemas (Pydantic v2)

### 2.1 Coordinate & Mask Primitives
```python
from typing import List, Optional
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    x_min: float = Field(..., description="Normalized top-left X coordinate [0.0 - 1.0]")
    y_min: float = Field(..., description="Normalized top-left Y coordinate [0.0 - 1.0]")
    x_max: float = Field(..., description="Normalized bottom-right X coordinate [0.0 - 1.0]")
    y_max: float = Field(..., description="Normalized bottom-right Y coordinate [0.0 - 1.0]")

class PolygonPoint(BaseModel):
    x: float = Field(..., description="Normalized X coordinate [0.0 - 1.0]")
    y: float = Field(..., description="Normalized Y coordinate [0.0 - 1.0]")
```

### 2.2 Detection Items
```python
class DetectedDefect(BaseModel):
    defect_id: int
    defect_type: DefectType
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: BoundingBox
    polygon: List[PolygonPoint]
    pixel_area: int = Field(..., description="Number of defect mask pixels")

class DetectedFruit(BaseModel):
    fruit_id: int
    fruit_type: str = Field(default="fruit", description="e.g. apple, citrus")
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: BoundingBox
    polygon: List[PolygonPoint]
    pixel_area: int = Field(..., description="Total fruit body mask pixels")
```

### 2.3 Timing Breakdown
```python
class InspectionTiming(BaseModel):
    preprocess_ms: float
    inference_ms: float
    postprocess_ms: float
    grading_ms: float
    total_ms: float
```

### 2.4 Complete Inspection Response Payload
```python
class InspectionResponse(BaseModel):
    inspection_id: str = Field(..., description="Unique UUID for this inspection event")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    image_width: int
    image_height: int
    fruit: Optional[DetectedFruit] = None
    defects: List[DetectedDefect] = Field(default_factory=list)
    defect_ratio_percent: float = Field(..., ge=0.0, le=100.0)
    grade: InspectionGrade
    reject_reason: Optional[str] = None
    timing: InspectionTiming
    overlay_image_base64: Optional[str] = Field(
        default=None, 
        description="Base64 encoded JPEG with annotated masks (if requested)"
    )
```

---

## 3. Database / Audit Log Schema (SQLite / DuckDB)

Table Name: `inspection_audit_logs`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | PRIMARY KEY | Unique inspection UUID |
| `timestamp` | DATETIME | NOT NULL | When inspection occurred |
| `model_version`| VARCHAR(50) | NOT NULL | Name/tag of ONNX model used |
| `fruit_type` | VARCHAR(50) | NULLABLE | Detected fruit type |
| `fruit_pixel_area` | INTEGER | NOT NULL | Total fruit mask pixels |
| `defect_pixel_area`| INTEGER | NOT NULL | Total defect mask pixels |
| `defect_ratio` | FLOAT | NOT NULL | Calculated defect area % |
| `grade` | VARCHAR(20) | NOT NULL | `PASS_GRADE_A`, `PASS_GRADE_B`, `REJECT` |
| `reject_reason`| VARCHAR(255)| NULLABLE | Reason string if rejected |
| `rot_count` | INTEGER | DEFAULT 0 | Count of active rot instances |
| `bruise_count` | INTEGER | DEFAULT 0 | Count of bruise instances |
| `total_latency_ms`| FLOAT | NOT NULL | End-to-end execution time in ms |
| `image_path` | VARCHAR(255)| NULLABLE | Path to archived frame |
