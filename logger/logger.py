import sqlite3
import requests
from datetime import datetime

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "database", "attacks.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            ip TEXT,
            attack_type TEXT,
            path TEXT,
            user_agent TEXT,
            payload TEXT,
            country TEXT,
            city TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_location(ip):
    try:
        if ip in ("127.0.0.1", "localhost", "::1"):
            return "Local", "Local"
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = resp.json()
        return data.get("country", "Unknown"), data.get("city", "Unknown")
    except:
        return "Unknown", "Unknown"

def log_attack(data: dict):
    init_db()
    country, city = get_location(data.get("ip", ""))
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO attacks 
        (timestamp, ip, attack_type, path, user_agent, payload, country, city)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        data.get("ip", "unknown"),
        data.get("attack_type", "unknown"),
        data.get("path", "/"),
        data.get("user_agent", ""),
        data.get("payload", ""),
        country,
        city
    ))
    conn.commit()
    conn.close()
    print(f"[LOG] {data.get('attack_type')} from {data.get('ip')} on {data.get('path')}")

def log_honeypot_interaction(data: dict):
    log_attack(data)

def get_all_attacks():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM attacks ORDER BY timestamp DESC LIMIT 100"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
