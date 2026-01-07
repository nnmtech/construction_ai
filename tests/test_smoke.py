import importlib
import os

from fastapi.testclient import TestClient


def test_app_starts_and_health_ok(tmp_path, monkeypatch):
    # Keep tests isolated from any local SQLite file.
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("LOG_FILE", str(tmp_path / "test.log"))
    monkeypatch.setenv("AUTO_CREATE_SCHEMA", "true")
    # Starlette's TestClient uses host "testserver" by default.
    # Ensure TrustedHostMiddleware allows it during tests.
    monkeypatch.setenv("ALLOWED_HOSTS", "localhost,127.0.0.1,*.localhost,testserver")

    # Import after env is set so settings/db pick it up.
    app_main = importlib.import_module("app.main")

    with TestClient(app_main.app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        payload = r.json()
        assert payload["status"] in {"ok", "degraded"}
        assert payload["database"] in {"connected", "disconnected"}

        docs = client.get("/api/docs")
        assert docs.status_code == 200
