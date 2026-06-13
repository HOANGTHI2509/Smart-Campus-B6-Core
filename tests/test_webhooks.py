"""
Unit Tests cho Webhook APIs (Task 3 - CICD)
============================================
Test các endpoint hứng dữ liệu từ B1 (IoT) và B4 (AI Vision).
Dùng FastAPI TestClient với SQLite in-memory để test mà không cần MySQL thật.
"""
import os
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

# Thiết lập biến môi trường test TRƯỚC KHI import app
# (bắt buộc vì database.py và dependencies.py đọc env khi import)
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-32-chars-minimum")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("B3_API_URL", "http://mock-b3/api/v1/gate/open")
os.environ.setdefault("B7_API_URL", "http://mock-b7/api/v1/alerts")

from app.main import app
from app.models.core_models import User, Device, AccessLog
from app.core.dependencies import get_session


# =============================================================
# FIXTURES - Setup môi trường test
# =============================================================

@pytest.fixture(name="test_engine")
def test_engine_fixture():
    """Tạo SQLite in-memory engine cho tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="test_session")
def test_session_fixture(test_engine):
    """Tạo database session cho mỗi test."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(test_session):
    """
    Tạo TestClient với database session được inject.
    Override dependency get_session để dùng SQLite thay vì MySQL.
    """
    def get_test_session():
        yield test_session

    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="sample_user")
def sample_user_fixture(test_session):
    """Tạo user mẫu trong database cho tests."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        full_name="Nguyễn Văn Test",
        student_id="SV001",
        card_uid="RFID_ABC123",
        hashed_password=pwd_context.hash("password123"),
        is_active=True
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


@pytest.fixture(name="inactive_user")
def inactive_user_fixture(test_session):
    """Tạo user bị khóa cho tests."""
    user = User(
        full_name="Trần Thị Bị Khóa",
        student_id="SV002",
        card_uid="RFID_LOCKED",
        is_active=False
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user


# =============================================================
# TEST: Health Check
# =============================================================

class TestHealthCheck:
    def test_root_returns_ok(self, client):
        """Test endpoint health check trả về status ok."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "B6" in data["message"]


# =============================================================
# TEST: Webhook B1 - IoT/RFID Events
# =============================================================

class TestWebhookB1:
    """Tests cho endpoint POST /api/v1/webhooks/iot-event"""

    BASE_URL = "/api/v1/webhooks/iot-event"

    def test_rfid_event_valid_card(self, client, sample_user):
        """Test quẹt thẻ RFID hợp lệ → Trả về success."""
        payload = {
            "eventType": "sensor.reading.created",
            "eventId": "test-uuid-001",
            "correlationId": "corr-uuid-001",
            "deviceId": "GATE-A-001",
            "sensorType": "rfid",
            "card_uid": "RFID_ABC123"  # Khớp với sample_user
        }
        response = client.post(self.BASE_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Nguyễn Văn Test" in data["message"]

    def test_rfid_event_unknown_card(self, client):
        """Test quẹt thẻ không tồn tại → Trả về error."""
        payload = {
            "eventType": "sensor.reading.created",
            "eventId": "test-uuid-002",
            "correlationId": "corr-uuid-002",
            "deviceId": "GATE-A-001",
            "sensorType": "rfid",
            "card_uid": "UNKNOWN_CARD_99"
        }
        response = client.post(self.BASE_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "không tồn tại" in data["message"].lower() or "chưa được đăng ký" in data["message"].lower()

    def test_rfid_event_locked_card(self, client, inactive_user):
        """Test quẹt thẻ của tài khoản bị khóa → Trả về error."""
        payload = {
            "eventType": "sensor.reading.created",
            "eventId": "test-uuid-003",
            "correlationId": "corr-uuid-003",
            "deviceId": "GATE-B-001",
            "sensorType": "rfid",
            "card_uid": "RFID_LOCKED"  # Khớp với inactive_user
        }
        response = client.post(self.BASE_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "khóa" in data["message"].lower()

    def test_sensor_reading_no_card_uid(self, client):
        """Test sự kiện cảm biến thường (không phải RFID) → Trả về ignored."""
        payload = {
            "eventType": "sensor.reading.created",
            "eventId": "test-uuid-004",
            "correlationId": "corr-uuid-004",
            "deviceId": "TEMP-SENSOR-001",
            "sensorType": "temperature",
            "value": 28.5,
            "unit": "°C"
            # Không có card_uid
        }
        response = client.post(self.BASE_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"

    @patch("app.services.outbound_api.send_alert_b7", new_callable=AsyncMock, return_value=True)
    def test_threshold_exceeded_sends_alert(self, mock_alert, client):
        """Test vượt ngưỡng cảm biến → Gửi cảnh báo sang B7."""
        payload = {
            "eventType": "sensor.threshold.exceeded",
            "eventId": "test-uuid-005",
            "correlationId": "corr-uuid-005",
            "deviceId": "SMOKE-001",
            "sensorType": "smoke",
            "value": 450.0,
            "threshold": 200.0,
            "unit": "ppm",
            "severity": "HIGH",
            "locationId": "ROOM-101"
        }
        response = client.post(self.BASE_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        # Kiểm tra outbound_api.send_alert_b7 đã được gọi
        mock_alert.assert_called_once()

    def test_device_status_changed(self, client):
        """Test sự kiện thiết bị thay đổi trạng thái → Ghi nhận thành công."""
        payload = {
            "eventType": "device.status.changed",
            "eventId": "test-uuid-006",
            "correlationId": "corr-uuid-006",
            "deviceId": "GATE-A-001"
        }
        response = client.post(self.BASE_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "GATE-A-001" in data["message"]

    def test_invalid_event_type(self, client):
        """Test loại sự kiện không hợp lệ → FastAPI trả về 422."""
        payload = {
            "eventType": "invalid.event.type",  # Không có trong enum
            "eventId": "test-uuid-007",
            "correlationId": "corr-uuid-007",
            "deviceId": "GATE-A-001"
        }
        response = client.post(self.BASE_URL, json=payload)
        
        # FastAPI tự validate enum và trả về 422 Unprocessable Entity
        assert response.status_code == 422

    def test_missing_required_fields(self, client):
        """Test thiếu trường bắt buộc → FastAPI trả về 422."""
        payload = {
            "eventType": "sensor.reading.created"
            # Thiếu eventId, correlationId, deviceId
        }
        response = client.post(self.BASE_URL, json=payload)
        assert response.status_code == 422


# =============================================================
# TEST: Webhook B4 - Tailgating Alert
# =============================================================

class TestWebhookB4:
    """Tests cho endpoint POST /api/v1/webhooks/tailgating"""

    BASE_URL = "/api/v1/webhooks/tailgating"

    @patch("app.services.outbound_api.send_alert_b7", new_callable=AsyncMock, return_value=True)
    def test_tailgating_alert_received(self, mock_alert, client):
        """Test nhận cảnh báo bám đuôi → Ghi nhận và forward sang B7."""
        payload = {
            "gate_id": "GATE-A-001",
            "detected_faces_count": 2,
            "alert_type": "tailgating",
            "confidence": 0.95,
            "timestamp": "2026-06-13T10:05:00Z"
        }
        response = client.post(self.BASE_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["received"] is True
        assert "GATE-A-001" in data["message"]
        assert data["alert_forwarded"] is True
        mock_alert.assert_called_once()

    @patch("app.services.outbound_api.send_alert_b7", new_callable=AsyncMock, return_value=True)
    def test_tailgating_high_severity_for_many_faces(self, mock_alert, client):
        """Test nhiều khuôn mặt → Mức cảnh báo cao hơn."""
        payload = {
            "gate_id": "GATE-MAIN",
            "detected_faces_count": 5,  # >= 5 → critical
            "alert_type": "tailgating"
        }
        response = client.post(self.BASE_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["received"] is True
        # Kiểm tra send_alert_b7 được gọi với severity=critical
        call_args = mock_alert.call_args
        assert call_args.kwargs.get("severity") == "critical" or call_args[1].get("severity") == "critical"

    @patch("app.services.outbound_api.send_alert_b7", new_callable=AsyncMock, return_value=False)
    def test_tailgating_b7_unavailable(self, mock_alert, client):
        """Test B7 không phản hồi → Vẫn trả về received=True nhưng alert_forwarded=False."""
        payload = {
            "gate_id": "GATE-B-002",
            "detected_faces_count": 3,
            "alert_type": "tailgating"
        }
        response = client.post(self.BASE_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["received"] is True
        assert data["alert_forwarded"] is False

    def test_tailgating_requires_min_2_faces(self, client):
        """Test phải có >= 2 khuôn mặt mới hợp lệ."""
        payload = {
            "gate_id": "GATE-A-001",
            "detected_faces_count": 1,  # < 2 → validation error
            "alert_type": "tailgating"
        }
        response = client.post(self.BASE_URL, json=payload)
        
        # FastAPI validate ge=2 constraint
        assert response.status_code == 422

    def test_tailgating_with_user_ids(self, client, sample_user):
        """Test cảnh báo kèm danh sách user_id."""
        with patch("app.services.outbound_api.send_alert_b7", new_callable=AsyncMock, return_value=True):
            payload = {
                "gate_id": "GATE-MAIN",
                "detected_faces_count": 2,
                "alert_type": "tailgating",
                "user_ids": ["SV001", "UNKNOWN"],
                "image_ref": "http://s3.example.com/evidence.jpg"
            }
            response = client.post(self.BASE_URL, json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["received"] is True

    def test_tailgating_missing_required_fields(self, client):
        """Test thiếu trường bắt buộc."""
        payload = {
            "detected_faces_count": 2
            # Thiếu gate_id
        }
        response = client.post(self.BASE_URL, json=payload)
        assert response.status_code == 422


# =============================================================
# TEST: Access Check API (kiểm tra thẻ từ)
# =============================================================

class TestAccessCheck:
    """Tests cho endpoint POST /api/v1/access/check"""

    BASE_URL = "/api/v1/access/check"

    def test_valid_card_grants_access(self, client, sample_user):
        """Test thẻ hợp lệ → is_granted = True."""
        payload = {
            "card_uid": "RFID_ABC123",
            "gate_id": "GATE-A-001"
        }
        response = client.post(self.BASE_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_granted"] is True
        assert data["status"] == "success"

    def test_unknown_card_denies_access(self, client):
        """Test thẻ không tồn tại → is_granted = False."""
        payload = {
            "card_uid": "UNKNOWN_CARD",
            "gate_id": "GATE-A-001"
        }
        response = client.post(self.BASE_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_granted"] is False
        assert data["status"] == "error"

    def test_locked_card_denies_access(self, client, inactive_user):
        """Test thẻ bị khóa → is_granted = False."""
        payload = {
            "card_uid": "RFID_LOCKED",
            "gate_id": "GATE-A-001"
        }
        response = client.post(self.BASE_URL, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_granted"] is False
        assert data["status"] == "error"
