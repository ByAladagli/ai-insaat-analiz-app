import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import REPORT_DIR, _validate_image, app
from fastapi import HTTPException

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_report_path_traversal_is_rejected():
    response = client.get("/download-report/../../main.py")
    assert response.status_code in (400, 404)


def test_unknown_report_is_404():
    response = client.get("/download-report/" + "0" * 32 + ".pdf")
    assert response.status_code == 404


def test_non_image_payload_is_rejected():
    try:
        _validate_image("parcel.png", b"this is not a real image")
    except HTTPException as exc:
        assert exc.status_code == 415
    else:
        raise AssertionError("Invalid image payload should be rejected")
