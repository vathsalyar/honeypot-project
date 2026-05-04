import os
import openpyxl

CALLBACK_URL = "http://127.0.0.1:5000/honeytoken-triggered"
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), "files")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_txt_token(filename="company_passwords.txt"):
    token_id = os.urandom(4).hex()
    content  = f"""# Company Credentials — STRICTLY CONFIDENTIAL
# Internal use only — Audited document ID: HT-{token_id}
# Last reviewed: 2024-03-01

[VPN Access]
Server   : vpn.corp.com
Username : corp_admin
Password : C0rpVPN@2024!

[Database]
Host     : db.internal.corp.com
Username : db_root
Password : Secur3DB_Pr0d!

[AWS Console]
Access Key : AKIAIOSFODNN7EXAMPLE
Secret Key : wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[SSH Key passphrase]
Key file : /root/.ssh/id_rsa
Passphrase : SSH_P@ss2024

# If you are reading this, you have accessed a monitored file.
# Notification sent to: security@corp.com
# Tracking URL: {CALLBACK_URL}?file=company_passwords&id={token_id}
"""
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    print(f"[+] Created: {path}")
    return path


def create_xlsx_token(filename="HR_salary_data.xlsx"):
    token_id = os.urandom(4).hex()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Salary 2024"

    # Fake data
    headers = ["Emp ID", "Full Name", "Department", "Annual Salary", "Bonus", "Manager"]
    ws.append(headers)
    rows = [
        ("E001", "Sarah Johnson",  "Engineering",  125000, 18000, "CTO"),
        ("E002", "Michael Chen",   "Finance",      115000, 15000, "CFO"),
        ("E003", "Priya Sharma",   "HR",            95000, 10000, "CHRO"),
        ("E004", "James Wilson",   "Engineering",  130000, 20000, "CTO"),
        ("E005", "Lisa Park",      "Marketing",     90000,  8000, "CMO"),
    ]
    for row in rows:
        ws.append(row)

    # Hidden tracking formula in column Z (fires when Excel opens the file)
    callback = f"{CALLBACK_URL}?file=salary&id={token_id}"
    ws["Z1"] = f'=HYPERLINK("{callback}","")'

    path = os.path.join(OUTPUT_DIR, filename)
    wb.save(path)
    print(f"[+] Created: {path}")
    return path


def create_pem_token(filename="ssh_private_keys.pem"):
    token_id = os.urandom(4).hex()
    content  = f"""-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA2a2rwplBQLF29amygykEMmYz0+Kcj3bKBp29BNObDcCH1um
YFBHbRyqDozJQxBNnIBXVU7S1oUwfJiG0bFMFSL8vwWoVrEG5MFAU/RRzFf7R
[HONEYTOKEN - ID: HT-{token_id}]
[Access logged — security@corp.com notified]
[Callback: {CALLBACK_URL}?file=ssh_keys&id={token_id}]
WkjQZkBHhQNJ7FHXOFd7KA9pPqgPiWYVME7AK4nCpvjBLGzQoXJCCSwbW5Ka9
-----END RSA PRIVATE KEY-----
"""
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    print(f"[+] Created: {path}")
    return path


if __name__ == "__main__":
    print("[*] Generating honeytoken files...")
    create_txt_token()
    create_xlsx_token()
    create_pem_token()
    print(f"\n[✓] All honeytokens saved to: {OUTPUT_DIR}")
