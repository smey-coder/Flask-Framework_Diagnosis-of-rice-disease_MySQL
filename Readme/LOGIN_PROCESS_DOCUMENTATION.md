# Login Process Implementation for Rice Disease Diagnosis System

## Overview
This document describes the complete login flow for the Flask application with three user roles: **Admin**, **Expert**, and **User**.

---

## Architecture

### 1. **Authentication Flow**

```
User Login → Validate Credentials → Check User Status → 
Role-Based Redirection → Dashboard (Admin/Expert/User)
```

### 2. **User Roles and Access Levels**

| Role | Purpose | Permissions | Dashboard |
|------|---------|-------------|-----------|
| **Admin** | System Management | Manage users, roles, permissions, system settings | `/admin/dashboard` |
| **Expert** | Create & Manage Rules | Create diagnosis rules, manage symptoms, diseases | `/expert/dashboard` |
| **User** | Use Diagnosis System | Access diagnosis tool, view results, history | `/user/dashboard` |

---

## Implementation Details

### **1. Login Route** (`app/routes/auth_routes.py`)

```python
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = UserTable.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash("Your account is inactive. Please contact administrator.", "warning")
                return redirect(url_for("auth.login"))

            login_user(user)
            flash(f"Welcome back, {user.full_name}!", "success")
            
            # Role-based redirection
            if user.has_role("Admin"):
                return redirect(url_for("admin.dashboard"))
            elif user.has_role("Expert"):
                return redirect(url_for("expert.dashboard"))
            else:
                # Default to user dashboard
                return redirect(url_for("user.dashboard"))

        flash("Invalid username or password.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")
```

**Key Features:**
- ✅ Username and password validation
- ✅ Account active status check
- ✅ Role-based redirection
- ✅ User-friendly flash messages
- ✅ CSRF protection

---

### **2. Admin Dashboard Route** (`app/routes/admin_route/__init__.py`)

```python
@admin_bp.route("/dashboard", methods=["GET"])
@login_required
@admin_required
def dashboard():
    """Admin dashboard page"""
    return render_template("admin_page/dashboard.html", user=current_user)
```

**Features:**
- Admin-only access with custom decorator
- Displays admin management options
- System statistics and quick actions

---

### **3. Expert Dashboard Route** (`app/routes/expert_route/__init__.py`)

```python
@expert_bp.route("/dashboard", methods=["GET"])
@login_required
@expert_required
def dashboard():
    """Expert dashboard page"""
    return render_template("expert_page/dashboard.html", user=current_user)
```

**Features:**
- Expert-only access with custom decorator
- Rule creation and management
- Disease and symptom management

---

### **4. User Dashboard Route** (`app/routes/user_route/__init__.py`)

```python
@user_bp.route("/dashboard", methods=["GET"])
@login_required
@user_required
def dashboard():
    """User dashboard page"""
    return render_template("user_page/dashboard.html", user=current_user)
```

**Features:**
- Default user access
- Diagnosis tool access
- Consultation history

---

## Role-Based Access Control

### **Admin Decorator**
```python
def admin_required(f):
    """Decorator to ensure user has Admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.has_role("Admin"):
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)
    return decorated_function
```

### **Expert Decorator**
```python
def expert_required(f):
    """Decorator to ensure user has Expert role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        if not current_user.has_role("Expert"):
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("user.dashboard"))
        return f(*args, **kwargs)
    return decorated_function
```

---

## Template Pages

### **Login Page** (`app/templates/auth/login.html`)
- Displays role information for clarity
- Username/password input fields
- "Forgot password" link
- "Sign up" link for new users
- Role badges showing access levels

### **Admin Dashboard** (`app/templates/admin_page/dashboard.html`)
- User management
- Disease management
- Symptom management
- Expert rules management

### **Expert Dashboard** (`app/templates/expert_page/dashboard.html`)
- Disease knowledge base
- Symptom field indicators
- Inference rules
- Consultation history

### **User Dashboard** (`app/templates/user_page/dashboard.html`)
- Diagnose option
- Disease information
- Treatment options
- Consultation history

---

## Database Model - User Roles

### **UserTable Model**
```python
class UserTable(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    roles = db.relationship("RoleTable", secondary=tbl_user_roles, back_populates="users")
    
    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)
```

### **RoleTable Model**
```python
class RoleTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    users = db.relationship("UserTable", secondary=tbl_user_roles, back_populates="roles")
    permissions = db.relationship("PermissionTable", secondary=tbl_role_permissions, back_populates="roles")
```

---

## Login Flow Diagram

```
┌─────────────────┐
│   User Login    │ (GET /auth/login)
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│  Username/Password   │ (POST /auth/login)
│   Validation         │
└────────┬─────────────┘
         │
    ┌────┴────┐
    │          │
    ▼          ▼
Success    Invalid
    │          │
    ▼          ▼
┌──────────┐ ┌──────────────────┐
│Check     │ │Flash Error Msg   │
│Active    │ │Redirect to Login │
└─┬────────┘ └──────────────────┘
  │
  ├─ No ──► Flash Warning, Redirect to Login
  │
  ├─ Yes
  │
  ▼
┌──────────────────┐
│  Check User Role │
└──┬──┬──┬─────────┘
   │  │  │
Admin│Expert│User
   │  │  │
   ▼  ▼  ▼
┌─┐ ┌─┐ ┌────────────┐
│A│ │E│ │  User      │
│D│ │X│ │ Dashboard  │
│M│ │P│ └────────────┘
│I│ │E│
│N│ │R│
│D│ │T│
│a│ │D│
│s│ │a│
│h│ │s│
│b│ │h│
│o│ │b│
│a│ │o│
│r│ │a│
│d│ │r│
│ │ │d│
└─┘ └─┘
```

---

## Security Features

✅ **CSRF Protection** - Implemented using Flask-WTF
✅ **Password Hashing** - Using werkzeug.security
✅ **Session Management** - Flask-Login user loader
✅ **Role-Based Access Control** - Custom decorators
✅ **Account Status Check** - Inactive user prevention
✅ **Login Required** - Flask-Login protection

---

## Testing Credentials

To test the login process, you need users with assigned roles:

### **Create Test Users** (in database or via admin panel)

```sql
-- Admin User
INSERT INTO tbl_users (username, email, full_name, is_active, password_hash)
VALUES ('admin_user', 'admin@example.com', 'Admin User', TRUE, '<hashed_password>');

-- Expert User
INSERT INTO tbl_users (username, email, full_name, is_active, password_hash)
VALUES ('expert_user', 'expert@example.com', 'Expert User', TRUE, '<hashed_password>');

-- Regular User
INSERT INTO tbl_users (username, email, full_name, is_active, password_hash)
VALUES ('regular_user', 'user@example.com', 'Regular User', TRUE, '<hashed_password>');
```

Then assign roles via the association table `tbl_user_roles`.

---

## Session Management

**Login Session:**
- Session created via `login_user()`
- User data cached in Flask-Login
- Session expires on logout or browser close

**Logout:**
```python
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
```

---

## Routing Summary

| Route | Method | Purpose | Protection |
|-------|--------|---------|-----------|
| `/auth/login` | GET/POST | Login page & handler | None |
| `/auth/logout` | GET | Logout handler | `@login_required` |
| `/auth/register` | GET/POST | User registration | CSRF exempt |
| `/` | GET | Home redirect | Based on auth status |
| `/admin/dashboard` | GET | Admin panel | `@admin_required` |
| `/expert/dashboard` | GET | Expert panel | `@expert_required` |
| `/user/dashboard` | GET | User panel | `@login_required` |

---

## Files Modified/Created

1. ✅ `app/routes/auth_routes.py` - Updated login logic
2. ✅ `app/routes/admin_route/__init__.py` - Created admin routes
3. ✅ `app/routes/expert_route/__init__.py` - Created expert routes
4. ✅ `app/routes/user_route/__init__.py` - Created user routes
5. ✅ `app/templates/auth/login.html` - Updated with role info
6. ✅ `app/templates/user_page/dashboard.html` - Created user dashboard
7. ✅ `app/__init__.py` - Updated to register new blueprints

---

## Next Steps

1. **Create Admin, Expert, and User roles** in the database
2. **Assign roles to test users**
3. **Test login with different user types**
4. **Customize dashboard templates** based on role requirements
5. **Add role-based menu items** to navigation
6. **Implement permission checks** for specific features

---

## Notes

- The system uses Flask-Login for session management
- Each route is protected with role-based decorators
- Unauthorized access redirects to user dashboard with error message
- User roles are managed through the database association table
- All password hashes are stored securely

---

**Last Updated:** January 17, 2026
**Version:** 1.0
