import re

ATTACK_PATTERNS = {
    "sql_injection": [
        r"(\bSELECT\b|\bUNION\b|\bINSERT\b|\bDROP\b)",
        r"(--|;|'|\")(\s)*(OR|AND)\s*\d+=\d+",
        r"1=1|admin'--|or 1=1"
    ],
    "directory_traversal": [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",
        r"etc/passwd"
    ],
    "command_injection": [
        r"(;|\|)\s*(ls|cat|rm|wget|curl|bash|sh|whoami|id)",
        r"`[^`]+`"
    ],
    "xss": [
        r"<script.*?>",
        r"javascript:",
        r"onerror\s*="
    ]
}

def detect_attack(request_data: dict) -> dict:
    full_input = " ".join([
        request_data.get("path", ""),
        request_data.get("query", ""),
        request_data.get("body", ""),
        str(request_data.get("headers", ""))
    ])

    for attack_type, patterns in ATTACK_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, full_input, re.IGNORECASE):
                return {
                    "is_malicious": True,
                    "attack_type": attack_type,
                    "matched_pattern": pattern
                }

    return {
        "is_malicious": False,
        "attack_type": None,
        "matched_pattern": None
    }
