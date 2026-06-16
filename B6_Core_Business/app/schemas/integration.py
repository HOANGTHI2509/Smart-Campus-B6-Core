from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ==========================================
# DTO MODELS DÀNH CHO NHÓM B4 (AI VISION)
# ==========================================
class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int

class ObjectDetail(BaseModel):
    label: str
    confidence: float
    boundingBox: Optional[BoundingBox] = None

class DetectionResult(BaseModel):
    detectionId: str
    cameraId: str
    detectionType: str # "OBJECT" hoặc "FACE"
    detectedObjects: Optional[List[ObjectDetail]] = None
    riskLevel: str     # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    timestamp: datetime


# ==========================================
# DTO MODELS DÀNH CHO NHÓM B3 (ACCESS GATE)
# ==========================================
class AccessCheckRequest(BaseModel):
    gateId: str
    uid: str
    timestamp: datetime
