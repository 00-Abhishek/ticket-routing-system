from dashboard.utils import get_default_api_url, normalize_api_url
from pathlib import Path

import yaml


def test_backend_url_defaults_to_localhost(monkeypatch) -> None:
    monkeypatch.delenv("BACKEND_URL", raising=False)

    assert get_default_api_url() == "http://127.0.0.1:8000"


def test_backend_url_loads_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("BACKEND_URL", "http://backend:8000")

    assert get_default_api_url() == "http://backend:8000"


def test_backend_url_normalization_removes_trailing_slash() -> None:
    assert normalize_api_url(" http://backend:8000/ ") == "http://backend:8000"


def test_docker_compose_configuration() -> None:
    compose_path = Path(__file__).resolve().parents[1] / "docker-compose.yml"
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    backend = compose["services"]["backend"]
    dashboard = compose["services"]["dashboard"]

    assert backend["command"] == "uvicorn src.api.app:app --host 0.0.0.0 --port 8000"
    assert "8000:8000" in backend["ports"]
    assert "healthcheck" in backend
    assert "./data:/app/data" in backend["volumes"]
    assert "./models:/app/models" in backend["volumes"]
    assert "./reports:/app/reports" in backend["volumes"]

    assert dashboard["command"] == "streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port 8501"
    assert "8501:8501" in dashboard["ports"]
    assert dashboard["environment"]["BACKEND_URL"] == "http://backend:8000"
    assert dashboard["depends_on"]["backend"]["condition"] == "service_healthy"
