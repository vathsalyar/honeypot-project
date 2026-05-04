import requests
import time

BASE = "http://127.0.0.1:5000"

def separator(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print('='*55)

separator("TEST 1 — Normal clean request")
try:
    r = requests.get(f"{BASE}/home", timeout=5)
    print(f"  GET /home  →  Status: {r.status_code}")
    print(f"  Response preview: {r.text[:80]}")
except Exception as e:
    print(f"  Error: {e}")

time.sleep(1)

separator("TEST 2 — SQL Injection attack")
try:
    payload = "' OR 1=1 --"
    r = requests.get(f"{BASE}/login", params={"username": payload, "password": "x"}, timeout=5)
    print(f"  Payload: {payload}")
    print(f"  Status : {r.status_code}")
    print(f"  Preview: {r.text[:120]}")
except Exception as e:
    print(f"  Error: {e}")

time.sleep(1)

separator("TEST 3 — Directory Traversal")
try:
    r = requests.get(f"{BASE}/files?path=../../../etc/passwd", timeout=5)
    print(f"  GET /files?path=../../../etc/passwd")
    print(f"  Status : {r.status_code}")
    print(f"  Preview: {r.text[:120]}")
except Exception as e:
    print(f"  Error: {e}")

time.sleep(1)

separator("TEST 4 — Command Injection")
try:
    r = requests.get(f"{BASE}/search?q=hello;cat+/etc/passwd", timeout=5)
    print(f"  GET /search?q=hello;cat+/etc/passwd")
    print(f"  Status : {r.status_code}")
    print(f"  Preview: {r.text[:120]}")
except Exception as e:
    print(f"  Error: {e}")

time.sleep(1)

separator("TEST 5 — Attacker browses honeypot directly")
try:
    r = requests.get("http://127.0.0.1:5001/admin", timeout=5)
    print(f"  GET honeypot/admin  →  Status: {r.status_code}")
    print(f"  Preview: {r.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

time.sleep(1)

separator("TEST 6 — Honeytoken file accessed (insider threat)")
try:
    r = requests.get(
        f"{BASE}/honeytoken-triggered",
        params={"file": "HR_salary_data", "id": "demo-token-abc123"},
        timeout=5
    )
    print(f"  Honeytoken callback fired!")
    print(f"  Status: {r.status_code}")
    print(f"  → Alert sent to Telegram/Email (if configured)")
except Exception as e:
    print(f"  Error: {e}")

separator("DONE — Check dashboard at http://127.0.0.1:5173")
