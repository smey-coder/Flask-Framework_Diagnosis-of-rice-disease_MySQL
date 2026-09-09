import csv
import json
import os
from datetime import datetime, date
from decimal import Decimal
from flask import request, current_app, has_request_context
from flask_login import current_user
import pytz

AUDIT_FILENAME = "audit_log.csv"
AUDIT_FOLDERNAME = "audit_logs"
CAMBODIA_TZ = pytz.timezone("Asia/Phnom_Penh")


def default_json_serializer(obj):
    """Custom JSON serializer for non-standard data types like Decimal and datetime."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)
def get_audit_file_path():
    """Return absolute path of audit CSV file inside project and ensure headers exist safely."""
    folder_path = os.path.join(current_app.root_path, AUDIT_FOLDERNAME)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, AUDIT_FILENAME)
    # Safely create CSV with header if it doesn't exist
    if not os.path.exists(file_path):
        try:
            # Use 'x' mode (exclusive creation) to prevent race conditions across workers
            with open(file_path, mode="x", newline="", encoding="utf-8") as f:
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
        except FileExistsError:
            pass  # Created by another thread/process concurrently
    return file_path
def log_audit(action: str,
              table_name: str = "general",
              record_id: int = 0,
              before_data: dict = None,
              after_data: dict = None,
              description: str = None,
              details: dict = None):
    """
    Log audit event to CSV cleanly and reliably.
    Supports both standard CRUD payload and diagnosis/event-style dictionaries.
    """
    # 1. Merge description and details into after_data if provided
    if description or details:
        if after_data is None:
            after_data = {}
        if description:
            after_data["description"] = description
        if details:
            after_data["details"] = details
    file_path = get_audit_file_path()
    timestamp = datetime.now(CAMBODIA_TZ).isoformat()
    # 2. Extract authenticated or anonymous user info
    try:
        if current_user and current_user.is_authenticated:
            user_id = str(getattr(current_user, "id", "unknown"))
            email = getattr(current_user, "email", "unknown")
            try:
                roles = getattr(current_user, "roles", [])
                if isinstance(roles, list):
                    role_list = [r.name if hasattr(r, 'name') else str(r) for r in roles]
                    role = ", ".join(role_list) if role_list else "user"
                else:
                    role = str(roles)
            except Exception:
                role = "unknown"
        else:
            user_id = "anonymous"
            email = "anonymous"
            role = "anonymous"
    except Exception:
        user_id = "anonymous"
        email = "anonymous"
        role = "anonymous"

    # 3. Extract request metadata safely (with reverse proxy support)
    try:
        if has_request_context():
            # Support X-Forwarded-For if behind Nginx/Gunicorn
            if request.headers.get("X-Forwarded-For"):
                ip_address = request.headers.get("X-Forwarded-For").split(",")[0].strip()
            else:
                ip_address = request.remote_addr or "N/A"
            user_agent = (request.headers.get("User-Agent") or "N/A")[:300]
        else:
            ip_address = "N/A"
            user_agent = "N/A"
    except Exception:
        ip_address = "N/A"
        user_agent = "N/A"

    # 4. Safely serialize JSON payloads
    try:
        before_json = json.dumps(before_data, default=default_json_serializer, ensure_ascii=False) if before_data else ""
    except Exception:
        before_json = str(before_data)

    try:
        after_json = json.dumps(after_data, default=default_json_serializer, ensure_ascii=False) if after_data else ""
    except Exception:
        after_json = str(after_data)

    # 5. Append log entry to CSV
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
        print(f"[AUDIT LOG ERROR] Failed to write log: {str(e)}")