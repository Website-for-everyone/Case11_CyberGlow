"""
Unit and Smoke Tests for Case 11: CyberGlow Neon Studio
Verifies calculations, database operations, FastAPI endpoints, and bot handler registration.
"""

import pytest
import os
import sys

# Ensure project root is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from backend.app import app, compute_tube_metrics, generate_css_code
import database
from bot.bot import router, create_bot_and_dispatcher
from fastapi.testclient import TestClient

client = TestClient(app)

def test_tube_metrics_calculation_empty():
    metrics = compute_tube_metrics("")
    assert metrics["char_count"] == 0
    assert metrics["tube_length_m"] == 0.0
    assert metrics["total_price_rub"] == 0

def test_tube_metrics_calculation_standard():
    metrics = compute_tube_metrics("CYBER", font_name="Monoline Neon", height_cm=20.0)
    assert metrics["char_count"] == 5
    assert metrics["tube_length_m"] > 0
    assert metrics["power_watts"] >= 15
    assert metrics["total_price_rub"] >= 4900
    assert "x" in metrics["dimensions_cm"]

def test_tube_metrics_font_scaling():
    metrics_monoline = compute_tube_metrics("NEON", font_name="Monoline Neon", height_cm=20.0)
    metrics_script = compute_tube_metrics("NEON", font_name="Neon Script", height_cm=20.0)
    # Script font has loops and curves, so tube length must be greater
    assert metrics_script["tube_length_m"] > metrics_monoline["tube_length_m"]

def test_generate_css_code():
    css = generate_css_code("Tokyo Cyan", "Monoline Neon")
    assert "#00F0FF" in css
    assert "text-shadow" in css
    assert "neon-flicker" in css

def test_api_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "CYBERGLOW" in response.text

def test_api_catalog():
    response = client.get("/api/catalog")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert len(data["figures"]) >= 4

def test_api_calculate():
    payload = {
        "text": "OPEN 24/7",
        "font_name": "Tokyo Cyber",
        "height_cm": 25.0,
        "color_name": "Sakura Pink"
    }
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["metrics"]["char_count"] == 8
    assert "#FF007F" in data["css_code"]

def test_api_quote_validation():
    # Empty client name / contact must return 422
    response = client.post("/api/quote", json={"client_name": "", "contact": ""})
    assert response.status_code == 422

    # Valid quote
    payload = {
        "client_name": "Daniel",
        "contact": "@idrisov_prod",
        "sign_text": "BAR",
        "font_name": "Monoline Neon",
        "color_name": "Tokyo Cyan",
        "notes": "Test order"
    }
    response = client.post("/api/quote", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "quote_id" in data
    assert data["quote_id"] > 0

def test_database_figure_retrieval():
    fig = database.get_figure_by_slug("cyber_katana")
    assert fig is not None
    assert fig["price_rub"] == 14900
    assert fig["power_watts"] == 45

def test_bot_registration():
    bot, dp = create_bot_and_dispatcher()
    assert bot is not None
    assert dp is not None
    # Check that handlers are registered on the router
    assert len(router.message.handlers) >= 4
    assert len(router.callback_query.handlers) >= 5
