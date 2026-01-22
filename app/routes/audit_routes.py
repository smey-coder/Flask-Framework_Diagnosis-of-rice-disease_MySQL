from flask import Blueprint, render_template, request, current_app
import csv
import os
from datetime import datetime

audit_bp = Blueprint("audit", __name__, url_prefix="/admin/audit")


def get_audit_file_path():
    """Return absolute path to audit CSV file"""
    folder = os.path.join(current_app.root_path, "audit_logs")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "audit_log.csv")


def read_audit_logs():
    """Read all audit logs from CSV"""
    logs = []
    file_path = get_audit_file_path()
    if os.path.exists(file_path):
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row["timestamp"] = datetime.fromisoformat(row["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass
                logs.append(row)
    return logs


@audit_bp.route("/", methods=["GET"])
def index():
    logs = read_audit_logs()

    # Simple search/filter
    search_user = request.args.get("user_id", "").strip()
    search_action = request.args.get("action", "").strip().lower()
    if search_user:
        logs = [l for l in logs if l["user_id"] == search_user]
    if search_action:
        logs = [l for l in logs if l["action"].lower() == search_action]

    # Show latest first
    logs = logs[::-1]

    return render_template("audit_page/audit_logs.html", logs=logs)
