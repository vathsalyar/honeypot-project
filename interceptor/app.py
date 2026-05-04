import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, request, redirect, jsonify, Response, render_template, url_for
from flask_cors import CORS
import requests as http_requests

from interceptor.detector import detect_attack
from logger.logger      import log_attack, get_all_attacks
from alerts.alerter     import send_alert

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)

HONEYPOT_URL    = "http://127.0.0.1:5001"
REAL_SERVER_URL = "http://127.0.0.1:5002"

# ── Home: show the corporate login page ───────────────────────────────────
@app.route("/")
def index():
    return render_template("login.html")

# ── Login form submission ─────────────────────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    req_data = {
        "path":    "/login",
        "query":   "",
        "body":    f"username={username}&password={password}",
        "headers": dict(request.headers)
    }

    result = detect_attack(req_data)

    if result["is_malicious"]:
        log_attack({
            "ip":          request.remote_addr,
            "attack_type": result["attack_type"],
            "path":        "/login",
            "user_agent":  request.headers.get("User-Agent", ""),
            "payload":     f"username={username}"
        })
        send_alert(
            f"⚠️ LOGIN ATTACK DETECTED!\n"
            f"Type   : {result['attack_type']}\n"
            f"IP     : {request.remote_addr}\n"
            f"Payload: username={username}\n"
            f"Agent  : {request.headers.get('User-Agent','')}"
        )
        # Redirect attacker silently to honeypot admin panel
        return redirect(f"{HONEYPOT_URL}/admin-panel", code=302)

    # Legitimate login — just show error (no real auth needed for demo)
    return redirect("/?error=1")

# ── API endpoints for dashboard ───────────────────────────────────────────
@app.route("/api/attacks")
def api_attacks():
    return jsonify(get_all_attacks())

@app.route("/api/stats")
def api_stats():
    attacks    = get_all_attacks()
    by_type    = {}
    by_country = {}
    for a in attacks:
        t = a["attack_type"] or "unknown"
        c = a["country"]     or "Unknown"
        by_type[t]    = by_type.get(t, 0)    + 1
        by_country[c] = by_country.get(c, 0) + 1
    return jsonify({
        "total":      len(attacks),
        "by_type":    by_type,
        "by_country": by_country,
        "recent":     attacks[:5]
    })

# ── Honeytoken callback ────────────────────────────────────────────────────
@app.route("/honeytoken-triggered")
def honeytoken_alert():
    file_name = request.args.get("file", "unknown")
    token_id  = request.args.get("id",   "unknown")

    log_attack({
        "ip":          request.remote_addr,
        "attack_type": "HONEYTOKEN_ACCESS",
        "path":        f"/honeytoken/{file_name}",
        "user_agent":  request.headers.get("User-Agent", ""),
        "payload":     f"Token ID: {token_id}"
    })
    send_alert(
        f"🚨 HONEYTOKEN FILE OPENED!\n"
        f"File  : {file_name}\n"
        f"Token : {token_id}\n"
        f"IP    : {request.remote_addr}\n"
        f"This may be an INSIDER THREAT."
    )
    return "", 200

# ── Catch-all for other paths ─────────────────────────────────────────────
@app.route("/<path:path>", methods=["GET","POST","PUT","DELETE"])
def intercept(path):
    if path.startswith("api/") or path == "honeytoken-triggered":
        return jsonify({"error": "not found"}), 404

    req_data = {
        "path":    request.path,
        "query":   request.query_string.decode(),
        "body":    request.get_data(as_text=True),
        "headers": dict(request.headers)
    }

    result = detect_attack(req_data)

    if result["is_malicious"]:
        log_attack({
            "ip":          request.remote_addr,
            "attack_type": result["attack_type"],
            "path":        request.path,
            "user_agent":  request.headers.get("User-Agent", ""),
            "payload":     req_data["query"] or req_data["body"]
        })
        send_alert(
            f"⚠️ ATTACK DETECTED!\n"
            f"Type: {result['attack_type']}\n"
            f"IP  : {request.remote_addr}\n"
            f"Path: {request.path}"
        )
        try:
            hp = http_requests.get(f"{HONEYPOT_URL}/{path}", timeout=3)
            return Response(hp.content, status=hp.status_code,
                            content_type=hp.headers.get("Content-Type","text/html"))
        except:
            return redirect(f"{HONEYPOT_URL}/admin-panel")

    return f"<h2>Page not found: /{path}</h2>", 404

if __name__ == "__main__":
    print("[*] Interceptor running → http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
