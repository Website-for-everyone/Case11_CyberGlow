"""
CyberGlow Neon Studio — FastAPI Backend
Provides sign calculation, catalog access, CSS generation, and lead dispatch.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import math
import sys

# Add parent directory to sys.path for database imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

app = FastAPI(title="CyberGlow Neon Studio API", version="1.0.0")

# Mount static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

FONT_FACTORS = {
    "Monoline Neon": 1.0,
    "Tokyo Cyber": 1.15,
    "Neon Script": 1.35,
    "Retro Glow": 1.20,
    "Samurai Gothic": 1.25
}

COLOR_PALETTES = {
    "Tokyo Cyan": {"hex": "#00F0FF", "rgb": "0, 240, 255"},
    "Sakura Pink": {"hex": "#FF007F", "rgb": "255, 0, 127"},
    "Electric Lime": {"hex": "#39FF14", "rgb": "57, 255, 20"},
    "Ultraviolet": {"hex": "#9D00FF", "rgb": "157, 0, 255"},
    "Sunset Amber": {"hex": "#FF9900", "rgb": "255, 153, 0"},
    "Hyper Red": {"hex": "#FF0033", "rgb": "255, 0, 51"},
    "Ice White": {"hex": "#FFFFFF", "rgb": "255, 255, 255"}
}

def compute_tube_metrics(text: str, font_name: str = "Monoline Neon", height_cm: float = 20.0) -> Dict[str, Any]:
    cleaned = text.strip()
    if not cleaned:
        return {
            "char_count": 0,
            "tube_length_cm": 0.0,
            "tube_length_m": 0.0,
            "power_watts": 0,
            "recommended_psu": "12V 15W",
            "base_acrylic_rub": 0,
            "tube_cost_rub": 0,
            "total_price_rub": 0,
            "dimensions_cm": "0x0 cm"
        }
    
    font_factor = FONT_FACTORS.get(font_name, 1.1)
    
    # Complex character stroke estimates in cm at 20cm height
    char_length_cm = 0.0
    for ch in cleaned:
        if ch.isspace():
            continue
        elif ch.upper() in "MWQ&%$#":
            char_length_cm += 45.0
        elif ch.upper() in "BDRABGK890":
            char_length_cm += 38.0
        elif ch.upper() in "CEFHJLNOPRSTUVXYZ234567":
            char_length_cm += 32.0
        elif ch in ".,'!;:|-":
            char_length_cm += 12.0
        else:
            char_length_cm += 30.0

    # Scale with user height and font complexity
    scale = height_cm / 20.0
    total_length_cm = char_length_cm * font_factor * scale
    total_length_m = round(total_length_cm / 100.0, 2)
    
    # Power consumption: 12 Watts per meter + 15W overhead
    raw_watts = math.ceil(total_length_m * 12.0)
    power_watts = max(15, raw_watts)
    
    if power_watts <= 36:
        psu = "12V 36W Slim"
    elif power_watts <= 60:
        psu = "12V 60W IP67"
    elif power_watts <= 100:
        psu = "12V 100W UltraThin"
    else:
        psu = "12V 150W Industrial"

    # Price formula: Base acrylic ₽2,500 + ₽1,800/meter + PSU ₽1,200 + Assembly ₽1,500
    base_acrylic = 2500
    tube_cost = math.ceil(total_length_m * 1800)
    psu_cost = 1200
    assembly = 1500
    calc_total = base_acrylic + tube_cost + psu_cost + assembly
    
    # Enforce minimum order threshold
    total_price = max(4900, calc_total)
    
    approx_width_cm = math.ceil(len(cleaned) * (height_cm * 0.7))
    approx_height_cm = math.ceil(height_cm * (cleaned.count("\n") + 1))

    return {
        "char_count": len([c for c in cleaned if not c.isspace()]),
        "tube_length_cm": round(total_length_cm, 1),
        "tube_length_m": total_length_m,
        "power_watts": power_watts,
        "recommended_psu": psu,
        "base_acrylic_rub": base_acrylic,
        "tube_cost_rub": tube_cost,
        "total_price_rub": total_price,
        "dimensions_cm": f"{approx_width_cm}x{approx_height_cm} cm"
    }

def generate_css_code(color_name: str, font_name: str) -> str:
    color_info = COLOR_PALETTES.get(color_name, COLOR_PALETTES["Tokyo Cyan"])
    r_g_b = color_info["rgb"]
    hex_val = color_info["hex"]
    
    return f"""/* CyberGlow Neon Text Shadow Effect */
.cyberglow-neon {{
  font-family: '{font_name}', 'Orbitron', sans-serif;
  color: #FFFFFF;
  text-shadow:
    0 0 5px #FFFFFF,
    0 0 10px #FFFFFF,
    0 0 20px {hex_val},
    0 0 40px {hex_val},
    0 0 80px rgba({r_g_b}, 0.8),
    0 0 120px rgba({r_g_b}, 0.5);
  filter: drop-shadow(0 0 15px rgba({r_g_b}, 0.9));
  animation: neon-flicker 3s infinite alternate;
}}

@keyframes neon-flicker {{
  0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {{
    opacity: 1;
    filter: drop-shadow(0 0 18px rgba({r_g_b}, 0.95));
  }}
  20%, 24%, 55% {{
    opacity: 0.6;
    filter: none;
  }}
}}"""

# Schemas
class CalculateRequest(BaseModel):
    text: str
    font_name: str = "Monoline Neon"
    height_cm: float = 20.0
    color_name: str = "Tokyo Cyan"

class QuoteRequest(BaseModel):
    client_name: str
    contact: str
    sign_text: Optional[str] = ""
    font_name: Optional[str] = "Monoline Neon"
    color_name: Optional[str] = "Tokyo Cyan"
    wall_texture: Optional[str] = "brick"
    height_cm: Optional[float] = 20.0
    notes: Optional[str] = ""

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>CyberGlow Backend is active</h1><p>UI loading...</p>")

@app.get("/api/catalog")
async def get_catalog():
    figures = database.get_all_figures()
    return {"status": "ok", "figures": figures}

@app.post("/api/calculate")
async def api_calculate(req: CalculateRequest):
    metrics = compute_tube_metrics(req.text, req.font_name, req.height_cm)
    css_code = generate_css_code(req.color_name, req.font_name)
    return {
        "status": "ok",
        "metrics": metrics,
        "css_code": css_code
    }

@app.post("/api/quote")
async def api_submit_quote(req: QuoteRequest):
    if not req.client_name.strip() or not req.contact.strip():
        raise HTTPException(status_code=422, detail="Имя и контактные данные обязательны")
    
    metrics = compute_tube_metrics(req.sign_text or "Neon", req.font_name or "Monoline Neon", req.height_cm or 20.0)
    
    quote_data = {
        "client_name": req.client_name,
        "contact": req.contact,
        "sign_text": req.sign_text,
        "font_name": req.font_name,
        "color_name": req.color_name,
        "wall_texture": req.wall_texture,
        "tube_length_m": metrics["tube_length_m"],
        "power_watts": metrics["power_watts"],
        "total_price_rub": metrics["total_price_rub"],
        "notes": req.notes,
        "photo_file_id": None
    }
    quote_id = database.save_quote(quote_data)
    
    lead_payload = {
        "project_name": "CyberGlow",
        "lead_type": "custom_neon_quote",
        "client_data": {
            "name": req.client_name,
            "contact": req.contact,
            "text": req.sign_text,
            "font": req.font_name,
            "color": req.color_name,
            "wall": req.wall_texture,
            "price": metrics["total_price_rub"]
        },
        "target_recipient": "@Idrisov_prod",
        "quote_id": quote_id
    }
    
    return {
        "status": "ok",
        "quote_id": quote_id,
        "metrics": metrics,
        "lead_payload": lead_payload,
        "message": "Заявка успешно зарегистрирована. Мастер CyberGlow свяжется с вами в течение 15 минут!"
    }
