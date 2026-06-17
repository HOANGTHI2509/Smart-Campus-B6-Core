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

# ==========================================
# DTO MODELS DÀNH CHO NHÓM B2 (CAMERA STREAM)
# ==========================================
class CameraDetection(BaseModel):
    label: str
    confidence: float

class CameraEvent(BaseModel):
    sourceService: str
    eventType: str
    cameraId: str
    frameId: str
    snapshotUrl: Optional[str] = None
    timestamp: datetime
    processedAt: datetime
    motionScore: float
    quality: Optional[str] = None
    detections: List[CameraDetection]
    objectCount: int
    labels: List[str]
    maxConfidence: float
    abnormal: bool
    severity: str
