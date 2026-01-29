# app/decorators/access.py
from functools import wraps
from flask import redirect, url_for, flash, has_request_context
from flask_login import current_user

def role_required(*role_names):
    """Allow multiple roles for a route."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not has_request_context():
                raise RuntimeError("role_required decorator used outside request context")

            if not current_user.is_authenticated:
                flash("Please log in first.", "warning")
                return redirect(url_for("auth.login"))

            if not any(getattr(current_user, "has_role", lambda r: False)(role) for role in role_names):
                flash("You do not have the required role.", "danger")
                # Redirect to the proper dashboard if role exists
                if getattr(current_user, "has_role", lambda r: False)("Admin"):
                    return redirect(url_for("admin.dashboard"))
                elif getattr(current_user, "has_role", lambda r: False)("Expert"):
                    return redirect(url_for("expert.dashboard"))
                return redirect(url_for("auth.login"))

            return f(*args, **kwargs)
        return wrapped
    return decorator

def permission_required(*permission_codes):
    """Allow multiple permissions for a route."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not has_request_context():
                raise RuntimeError("permission_required decorator used outside request context")

            if not current_user.is_authenticated:
                flash("Please log in first.", "warning")
                return redirect(url_for("auth.login"))

            if not any(getattr(current_user, "has_permission", lambda p: False)(perm) for perm in permission_codes):
                flash("You do not have permission to perform this action.", "danger")
                # Redirect to dashboard based on role
                if getattr(current_user, "has_role", lambda r: False)("Admin"):
                    return redirect(url_for("admin.dashboard"))
                elif getattr(current_user, "has_role", lambda r: False)("Expert"):
                    return redirect(url_for("expert.dashboard"))
                return redirect(url_for("auth.login"))

            return f(*args, **kwargs)
        return wrapped
    return decorator
