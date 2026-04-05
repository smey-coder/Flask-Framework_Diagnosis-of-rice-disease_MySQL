"""
Custom decorators for authentication, authorization, and permission-based access control.

This module provides decorators for:
- Permission checking
- Role-based access control
- Route protection
- Admin/Expert access restrictions
"""

from functools import wraps
from typing import List, Union, Callable
from flask import flash, redirect, url_for, abort
from flask_login import current_user
from app.services.permission_role_service import PermissionRoleService


# ===================== ROLE-BASED ACCESS CONTROL =====================

def require_role(role_name: Union[str, List[str]]):
    """
    Decorator to require user to have a specific role or one of multiple roles.
    
    Usage:
        @app.route('/admin')
        @require_role('Admin')
        def admin_page():
            return 'Admin page'
        
        @app.route('/staff-area')
        @require_role(['Admin', 'Expert'])
        def staff_area():
            return 'Staff area'
    
    Args:
        role_name: Single role name (str) or list of role names (List[str])
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            
            # Convert single role to list
            roles = [role_name] if isinstance(role_name, str) else role_name
            
            # Check if user has any of the required roles
            if not any(current_user.has_role(role) for role in roles):
                flash("You do not have permission to access this page.", "danger")
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_admin():
    """
    Decorator to restrict access to Admin users only.
    
    Usage:
        @app.route('/admin-settings')
        @require_admin()
        def admin_settings():
            return 'Admin settings'
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            
            # Check if user has Admin role
            if not current_user.has_role("Admin"):
                flash("Admin access required.", "danger")
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_expert():
    """
    Decorator to restrict access to Expert users only.
    
    Usage:
        @app.route('/diagnosis')
        @require_expert()
        def diagnosis_page():
            return 'Diagnosis page'
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            
            # Check if user has Expert role
            if not current_user.has_role("Expert"):
                flash("Expert access required.", "danger")
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# ===================== PERMISSION-BASED ACCESS CONTROL =====================

def require_permission(permission_code: Union[str, List[str]], require_all: bool = False):
    """
    Decorator to require user to have specific permission(s).
    
    Usage:
        # Require single permission
        @app.route('/create-user')
        @require_permission('user.create')
        def create_user():
            return 'Create user page'
        
        # Require any of multiple permissions
        @app.route('/edit-content')
        @require_permission(['content.edit', 'content.manage'])
        def edit_content():
            return 'Edit content'
        
        # Require all permissions
        @app.route('/manage-system')
        @require_permission(['system.view', 'system.manage'], require_all=True)
        def manage_system():
            return 'Manage system'
    
    Args:
        permission_code: Single permission code (str) or list of codes (List[str])
        require_all: If True, user must have ALL permissions. If False, ANY permission suffices.
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            
            # Get user's primary role (first role assigned)
            user_roles = current_user.roles
            if not user_roles:
                flash("You do not have permission to access this page.", "danger")
                abort(403)
            
            user_role = user_roles[0]
            
            # Convert single permission to list
            permissions = [permission_code] if isinstance(permission_code, str) else permission_code
            
            # Check permissions
            has_access = False
            if require_all:
                # User must have ALL permissions
                has_access = PermissionRoleService.has_all_permissions(user_role, permissions)
            else:
                # User must have AT LEAST ONE permission
                has_access = PermissionRoleService.has_any_permission(user_role, permissions)
            
            if not has_access:
                flash("You do not have permission to access this page.", "danger")
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_any_permission(*permission_codes: str):
    """
    Decorator to require user to have at least one of the specified permissions.
    This is a more flexible version of require_permission with *args syntax.
    
    Usage:
        @app.route('/content')
        @require_any_permission('content.view', 'content.edit', 'content.delete')
        def manage_content():
            return 'Manage content'
    
    Args:
        *permission_codes: Variable number of permission code strings
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            
            # Get user's primary role
            user_roles = current_user.roles
            if not user_roles:
                flash("You do not have permission to access this page.", "danger")
                abort(403)
            
            user_role = user_roles[0]
            
            # Check if user has any of the permissions
            if not PermissionRoleService.has_any_permission(user_role, list(permission_codes)):
                flash("You do not have permission to access this page.", "danger")
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_all_permissions(*permission_codes: str):
    """
    Decorator to require user to have ALL of the specified permissions.
    
    Usage:
        @app.route('/system-settings')
        @require_all_permissions('system.view', 'system.edit', 'system.manage')
        def system_settings():
            return 'System settings'
    
    Args:
        *permission_codes: Variable number of permission code strings
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            
            # Get user's primary role
            user_roles = current_user.roles
            if not user_roles:
                flash("You do not have permission to access this page.", "danger")
                abort(403)
            
            user_role = user_roles[0]
            
            # Check if user has all permissions
            if not PermissionRoleService.has_all_permissions(user_role, list(permission_codes)):
                flash("You do not have permission to access this page.", "danger")
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# ===================== OPTIONAL PERMISSION CHECKING =====================

def check_permission(permission_code: str):
    """
    Decorator that checks permission but doesn't block access - just passes result to view.
    Useful for showing/hiding content conditionally in templates.
    
    Usage:
        @app.route('/dashboard')
        @check_permission('content.manage')
        def dashboard(has_permission=False):
            return render_template('dashboard.html', can_manage=has_permission)
    
    Args:
        permission_code: The permission code to check
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            has_permission = False
            
            # Check permission if user is authenticated
            if current_user.is_authenticated:
                user_roles = current_user.roles
                if user_roles:
                    user_role = user_roles[0]
                    has_permission = PermissionRoleService.has_permission(user_role, permission_code)
            
            # Pass permission status to view function
            return f(*args, has_permission=has_permission, **kwargs)
        
        return decorated_function
    return decorator


# ===================== ACTIVITY/OWNERSHIP CHECKS =====================

def owner_or_admin_required(owner_id_param: str = "user_id"):
    """
    Decorator to ensure user either owns the resource or is an Admin.
    
    Usage:
        @app.route('/profile/<int:user_id>/edit', methods=['GET', 'POST'])
        @owner_or_admin_required('user_id')
        def edit_profile(user_id):
            # Only owner or admin can access
            return 'Edit profile'
    
    Args:
        owner_id_param: Name of the URL parameter containing the owner ID
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            
            # Get owner ID from URL parameters
            owner_id = kwargs.get(owner_id_param)
            
            # Check if user is the owner or an admin
            is_owner = current_user.id == owner_id
            is_admin = current_user.has_role("Admin")
            
            if not (is_owner or is_admin):
                flash("You do not have permission to access this resource.", "danger")
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# ===================== CONDITIONAL/ADVANCED CHECKS =====================

def active_user_required():
    """
    Decorator to ensure user account is active.
    
    Usage:
        @app.route('/consultation')
        @active_user_required()
        def start_consultation():
            return 'Start consultation'
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            
            # Check if user account is active
            if not current_user.is_active:
                flash("Your account has been deactivated. Please contact administrator.", "danger")
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def role_or_permission_required(role_name: str = None, permission_code: str = None):
    """
    Decorator to require either a specific role OR a specific permission.
    Useful for flexible access control.
    
    Usage:
        # User must be Admin OR have 'diagnosis.create' permission
        @app.route('/new-diagnosis')
        @role_or_permission_required(role_name='Expert', permission_code='diagnosis.create')
        def create_diagnosis():
            return 'Create diagnosis'
    
    Args:
        role_name: Required role name (can be None)
        permission_code: Required permission code (can be None)
    
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))
            
            has_access = False
            
            # Check role if specified
            if role_name and current_user.has_role(role_name):
                has_access = True
            
            # Check permission if specified
            if not has_access and permission_code:
                user_roles = current_user.roles
                if user_roles:
                    user_role = user_roles[0]
                    if PermissionRoleService.has_permission(user_role, permission_code):
                        has_access = True
            
            if not has_access:
                flash("You do not have permission to access this page.", "danger")
                abort(403)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
