import json
from datetime import datetime as real_datetime

import app as diun_app
import pytest


def _frozen_datetime(timestamp_seconds: int):
    """Produce an object with a static now() used to simulate clock shifts."""

    class _FrozenDatetime:
        @staticmethod
        def now():
            return real_datetime.fromtimestamp(timestamp_seconds)

    return _FrozenDatetime


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Isolate storage per test run.
    storage_path = tmp_path / "updates.json"
    monkeypatch.setattr(diun_app, "STORAGE_FILE", str(storage_path))
    diun_app.init_storage()
    diun_app.app.config["TESTING"] = True
    with diun_app.app.test_client() as flask_client:
        yield flask_client


def test_health_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "tracker is running" in response.get_data(as_text=True)


def test_webhook_stores_update_and_lists(client, monkeypatch):
    # Freeze time to keep deterministic detected_at.
    monkeypatch.setattr(diun_app, "datetime", _frozen_datetime(1_700_000_000))
    payload = {"image": "repo/app:1.0.0", "status": "update"}

    post_response = client.post("/webhook", json=payload)
    assert post_response.status_code == 200

    list_response = client.get("/updates/list")
    assert list_response.status_code == 200
    updates = list_response.get_json()
    assert len(updates) == 1
    assert updates[0]["image"] == "repo/app:1.0.0"
    assert updates[0]["status"] == "update"
    assert updates[0]["detected_at"] == pytest.approx(1_700_000_000 * 1000)

    # Summary should reflect the same record.
    summary_response = client.get("/updates/summary")
    assert summary_response.status_code == 200
    summary = summary_response.get_json()
    assert summary["total"] == 1
    assert summary["latest_image"] == "repo/app:1.0.0"
    assert summary["latest_status"] == "update"


def test_new_scan_clears_stale_updates(client, monkeypatch):
    early_time = 1_700_000_000
    late_time = early_time + (2 * 60 * 60)  # 2 hours later

    monkeypatch.setattr(diun_app, "datetime", _frozen_datetime(early_time))
    client.post("/webhook", json={"image": "repo/old:1.0.0", "status": "update"})

    monkeypatch.setattr(diun_app, "datetime", _frozen_datetime(late_time))
    client.post("/webhook", json={"image": "repo/new:2.0.0", "status": "update"})

    updates = client.get("/updates/list").get_json()
    assert [u["image"] for u in updates] == ["repo/new:2.0.0"]
    assert updates[0]["status"] == "update"

    summary = client.get("/updates/summary").get_json()
    assert summary["total"] == 1
    assert summary["latest_image"] == "repo/new:2.0.0"
