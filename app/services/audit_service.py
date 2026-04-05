import csv
import json
import os
from datetime import datetime
from flask import request, current_app, has_request_context
from flask_login import current_user
import pytz

AUDIT_FILENAME = "audit_log.csv"
AUDIT_FOLDERNAME = "audit_logs"
CAMBODIA_TZ = pytz.timezone("Asia/Phnom_Penh")


def get_audit_file_path():
    """Return absolute path of audit CSV file inside project"""
    folder_path = os.path.join(current_app.root_path, AUDIT_FOLDERNAME)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, AUDIT_FILENAME)

    # Create CSV with header if not exist
    if not os.path.exists(file_path):
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow([
                "timestamp",
                "user_id",
                "role",
                "email",
                "action",
                "table_name",
                "record_id",
                "before_data",
                "after_data",
                "ip_address",
                "user_agent"
            ])
    return file_path


def log_audit(action: str,
              table_name: str,
              record_id: int,
              before_data: dict = None,
              after_data: dict = None):
    """
    Log audit event to CSV
    """
    file_path = get_audit_file_path()
    timestamp = datetime.now(CAMBODIA_TZ).isoformat()

    # User info
    if current_user.is_authenticated:
        user_id = getattr(current_user, "id", "unknown")
        email = getattr(current_user, "email", "unknown")
        try:
            role_list = [role.name for role in getattr(current_user, "roles", [])]
            role = ", ".join(role_list) if role_list else "unknown"
        except Exception:
            role = "unknown"
    else:
        user_id = "anonymous"
        email = "anonymous"
        role = "anonymous"

    # Request info
    if has_request_context():
        ip_address = request.remote_addr
        user_agent = (request.headers.get("User-Agent") or "N/A")[:300]
    else:
        ip_address = "N/A"
        user_agent = "N/A"

    before_json = json.dumps(before_data, ensure_ascii=False) if before_data else ""
    after_json = json.dumps(after_data, ensure_ascii=False) if after_data else ""

    try:
        with open(file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow([
                timestamp,
                user_id,
                role,
                email,
                action,
                table_name,
                record_id,
                before_json,
                after_json,
                ip_address,
                user_agent
            ])
    except Exception as e:
        print(f"[AUDIT LOG ERROR] {str(e)}")
