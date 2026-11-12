"""
CyberGlow Neon Studio — SQLite Database Engine
Stores catalog items, custom sign quotes, and lead requests.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "cyberglow.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table for neon figures catalog
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS catalog_figures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        dimensions TEXT NOT NULL,
        tube_length_m REAL NOT NULL,
        power_watts INTEGER NOT NULL,
        price_rub INTEGER NOT NULL,
        description TEXT NOT NULL,
        color_primary TEXT NOT NULL,
        color_secondary TEXT NOT NULL,
        icon_svg TEXT
    )
    """)
    
    # Table for user custom sign quotes & orders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        contact TEXT NOT NULL,
        sign_text TEXT,
        font_name TEXT,
        color_name TEXT,
        wall_texture TEXT,
        tube_length_m REAL NOT NULL,
        power_watts INTEGER NOT NULL,
        total_price_rub INTEGER NOT NULL,
        notes TEXT,
        photo_file_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending'
    )
    """)
    
    # Pre-populate default figures if empty
    cursor.execute("SELECT COUNT(*) FROM catalog_figures")
    if cursor.fetchone()[0] == 0:
        default_figures = [
            ("Cyber Katana", "cyber_katana", "110x30 cm", 3.8, 45, 14900, "Неоновая катана в стиле Киберпанк с лезвием цвета ледяного циана", "#00F0FF", "#FF007F", "katana"),
            ("Angel Wings", "angel_wings", "120x80 cm", 6.2, 75, 24500, "Пара сияющих ангельских крыльев для фотозон и студий", "#FF007F", "#FFFFFF", "wings"),
            ("Tokyo Cocktail", "tokyo_cocktail", "45x55 cm", 2.4, 30, 9900, "Бокал мартини с неоновой оливкой и ярким лаймовым свечением", "#39FF14", "#FF007F", "cocktail"),
            ("Cyber Skull", "cyber_skull", "60x70 cm", 4.1, 50, 16900, "Анатомический неоновый череп с бирюзовыми глазницами", "#00F0FF", "#9D00FF", "skull"),
            ("Infinity Heart", "infinity_heart", "50x45 cm", 2.1, 25, 8900, "Пылающее неоновое сердце с градиентом розового и ультрафиолета", "#FF007F", "#FF9900", "heart"),
            ("Coffee Cloud", "coffee_cloud", "55x50 cm", 2.8, 35, 11500, "Дымящаяся чашка кофе для кофеен, баров и лофтов", "#FF9900", "#FFFFFF", "coffee"),
        ]
        cursor.executemany("""
        INSERT INTO catalog_figures 
        (title, slug, dimensions, tube_length_m, power_watts, price_rub, description, color_primary, color_secondary, icon_svg)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, default_figures)
        
    conn.commit()
    conn.close()

def get_all_figures() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM catalog_figures ORDER BY price_rub ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_figure_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM catalog_figures WHERE slug = ?", (slug,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_quote(data: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO quotes 
    (client_name, contact, sign_text, font_name, color_name, wall_texture, tube_length_m, power_watts, total_price_rub, notes, photo_file_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("client_name", "Anonymous"),
        data.get("contact", "N/A"),
        data.get("sign_text", ""),
        data.get("font_name", "Monoline Neon"),
        data.get("color_name", "Tokyo Cyan"),
        data.get("wall_texture", "brick"),
        data.get("tube_length_m", 0.0),
        data.get("power_watts", 0),
        data.get("total_price_rub", 0),
        data.get("notes", ""),
        data.get("photo_file_id", None)
    ))
    quote_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return quote_id

def get_quote_by_id(quote_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quotes WHERE id = ?", (quote_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Initialize upon module import
init_db()
