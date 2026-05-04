import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, request, render_template, Response
from logger.logger import log_honeypot_interaction

app = Flask(__name__, template_folder='templates')

FAKE_FILES = {
    "admin_passwords.txt": (
        "# NexaCorp Admin Credentials — TOP SECRET\n"
        "# Generated: 2024-01-15 | Owner: IT Security\n\n"
        "admin      : Admin@Nexa2024!\n"
        "root       : R00tS3cur3#99\n"
        "dbadmin    : DB@dmin_Pr0d!\n"
        "sysadmin   : SysP@ss$2024\n"
        "backup_usr : Backp#Secure1\n"
    ),
    "salary_data.xlsx": (
        "[Binary Excel File]\n"
        "NexaCorp Employee Salary Data 2024\n"
        "Records: 348 employees\n"
        "Last modified: 2024-03-01\n"
        "Classification: CONFIDENTIAL\n"
    ),
    "server_backup.sql": (
        "-- NexaCorp Production DB Backup\n"
        "-- Host: db.internal.nexacorp.com\n"
        "-- Generated: 2024-01-15 02:00:01\n\n"
        "CREATE TABLE users (id INT, username VARCHAR(50), password_hash VARCHAR(255), role VARCHAR(20));\n"
        "INSERT INTO users VALUES (1,'admin','5f4dcc3b5aa765d61d8327deb882cf99','superadmin');\n"
        "INSERT INTO users VALUES (2,'j.smith','482c811da5d5b4bc6d497ffa98491e38','user');\n"
    ),
    "ssh_private_keys.pem": (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA2a2rwplBQLzogPxMH3YCFMkuMmKkPGnMGwbEZDR7HONEYTOKEN\n"
        "WkjQZkBHhQNJ7FHXOFd7KA9pPqgPiWYVME7AK4nCpvjBLGzQoXJCCSwbW5Ka9Lm\n"
        "[TRACKED — security@nexacorp.com notified on access]\n"
        "-----END RSA PRIVATE KEY-----\n"
    ),
    "config.php": (
        "<?php\n"
        "// NexaCorp Production Config\n"
        "$db_host = 'db.internal.nexacorp.com';\n"
        "$db_name = 'nexacorp_prod';\n"
        "$db_user = 'prod_admin';\n"
        "$db_pass = 'Pr0d_S3cr3t#2024';\n"
        "$aws_key = 'AKIAIOSFODNN7EXAMPLE';\n"
        "$aws_sec = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY';\n"
        "?>\n"
    )
}

@app.route("/admin-panel")
@app.route("/admin-panel/<path:subpath>")
def admin_panel(subpath=""):
    log_honeypot_interaction({
        "ip":          request.remote_addr,
        "attack_type": "HONEYPOT_BROWSE",
        "path":        "/admin-panel/" + subpath,
        "user_agent":  request.headers.get("User-Agent", ""),
        "payload":     "Attacker redirected to honeypot admin panel"
    })
    return render_template("fake_admin.html")

@app.route("/download/<filename>")
def download_file(filename):
    log_honeypot_interaction({
        "ip":          request.remote_addr,
        "attack_type": "HONEYPOT_FILE_DOWNLOAD",
        "path":        f"/download/{filename}",
        "user_agent":  request.headers.get("User-Agent", ""),
        "payload":     f"Attacker tried to download: {filename}"
    })

    from alerts.alerter import send_alert
    send_alert(
        f"📁 HONEYPOT FILE DOWNLOAD ATTEMPT!\n"
        f"File  : {filename}\n"
        f"IP    : {request.remote_addr}\n"
        f"Agent : {request.headers.get('User-Agent','')}"
    )

    content = FAKE_FILES.get(filename, "File not found.")
    return Response(content, mimetype="text/plain",
                    headers={"Content-Disposition": f"attachment; filename={filename}"})

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    log_honeypot_interaction({
        "ip":          request.remote_addr,
        "attack_type": "HONEYPOT_BROWSE",
        "path":        "/" + path,
        "user_agent":  request.headers.get("User-Agent", ""),
        "payload":     request.query_string.decode()
    })
    return render_template("fake_admin.html")

if __name__ == "__main__":
    print("[*] Honeypot running → http://127.0.0.1:5001")
    app.run(host="0.0.0.0", port=5001, debug=True)
