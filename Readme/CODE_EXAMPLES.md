# Login System - Code Examples & Usage

## Common Usage Patterns

### 1. Check User Role in View

```python
from flask import render_template, redirect, url_for
from flask_login import current_user, login_required

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.has_role("Admin"):
        return render_template("admin_dashboard.html")
    elif current_user.has_role("Expert"):
        return render_template("expert_dashboard.html")
    else:
        return render_template("user_dashboard.html")
```

### 2. Check User Permission

```python
from flask_login import current_user

@app.route("/manage-users")
@login_required
def manage_users():
    if not current_user.has_permission("manage_users"):
        flash("You don't have permission to manage users", "danger")
        return redirect(url_for("user.dashboard"))
    
    # Display user management interface
    return render_template("admin/users/index.html")
```

### 3. Get All User Roles

```python
from flask_login import current_user

def get_user_roles():
    """Get all roles for current user"""
    return [role.name for role in current_user.roles]

# Usage
roles = get_user_roles()  # Returns ["Admin", "Expert"]
```

### 4. Get All User Permissions

```python
from flask_login import current_user

def get_user_permissions():
    """Get all permissions for current user"""
    return current_user.get_permission_code()

# Usage
permissions = get_user_permissions()  # Returns {"view_users", "manage_users", ...}
```

### 5. Check if User is Admin

```python
from flask_login import current_user

if current_user.has_role("Admin"):
    # Show admin options
    print("User is Admin")
else:
    # Hide admin options
    print("User is not Admin")
```

---

## Template Examples

### 1. Show Content Based on Role

```html
<!-- Show only to Admin -->
{% if current_user.has_role("Admin") %}
    <div class="admin-panel">
        <a href="/admin/users">Manage Users</a>
        <a href="/admin/settings">System Settings</a>
    </div>
{% endif %}

<!-- Show only to Expert -->
{% if current_user.has_role("Expert") %}
    <div class="expert-panel">
        <a href="/expert/rules">Create Rules</a>
        <a href="/expert/diseases">Manage Diseases</a>
    </div>
{% endif %}

<!-- Show to all authenticated users -->
{% if current_user.is_authenticated %}
    <div class="user-panel">
        Welcome, {{ current_user.full_name }}!
    </div>
{% endif %}
```

### 2. Role Badge Display

```html
<!-- Display user's roles -->
<div class="user-info">
    <h5>{{ current_user.full_name }}</h5>
    <div class="roles">
        {% for role in current_user.roles %}
            {% if role.name == "Admin" %}
                <span class="badge bg-danger">{{ role.name }}</span>
            {% elif role.name == "Expert" %}
                <span class="badge bg-success">{{ role.name }}</span>
            {% else %}
                <span class="badge bg-info">{{ role.name }}</span>
            {% endif %}
        {% endfor %}
    </div>
</div>
```

### 3. Conditional Navigation Menu

```html
<nav class="navbar">
    <ul class="nav-menu">
        {% if current_user.is_authenticated %}
            <li><a href="/">Home</a></li>
            
            {% if current_user.has_role("Admin") %}
                <li><a href="/admin/dashboard">Admin Panel</a></li>
                <li><a href="/admin/users">Users</a></li>
                <li><a href="/admin/roles">Roles</a></li>
            {% endif %}
            
            {% if current_user.has_role("Expert") %}
                <li><a href="/expert/dashboard">Expert Panel</a></li>
                <li><a href="/expert/rules">Rules</a></li>
            {% endif %}
            
            <li><a href="/user/dashboard">My Dashboard</a></li>
            <li><a href="/auth/logout">Logout</a></li>
        {% else %}
            <li><a href="/auth/login">Login</a></li>
            <li><a href="/auth/register">Register</a></li>
        {% endif %}
    </ul>
</nav>
```

---

## Database Queries

### 1. Get User with Roles

```python
from app.models.user import UserTable

# Get user and their roles
user = UserTable.query.filter_by(username="john_doe").first()
print(user.roles)  # [<Role Admin>, <Role Expert>]
```

### 2. Find All Users with Specific Role

```python
from app.models.user import UserTable
from app.models.role import RoleTable
from app.models.associations import tbl_user_roles

# Get all admin users
admin_role = RoleTable.query.filter_by(name="Admin").first()
admin_users = admin_role.users

for user in admin_users:
    print(user.username)
```

### 3. Get User by Email and Validate

```python
from app.models.user import UserTable

user = UserTable.query.filter_by(email="user@example.com").first()

if user and user.check_password("password123"):
    print("Valid credentials")
else:
    print("Invalid credentials")
```

### 4. Create User with Role

```python
from app.models.user import UserTable
from app.models.role import RoleTable
from extensions import db

# Create new user
user = UserTable(
    username="newuser",
    email="newuser@example.com",
    full_name="New User"
)
user.set_password("securepassword")

# Assign role
user_role = RoleTable.query.filter_by(name="User").first()
user.roles.append(user_role)

# Save to database
db.session.add(user)
db.session.commit()
```

### 5. Update User Roles

```python
from app.models.user import UserTable
from app.models.role import RoleTable
from extensions import db

user = UserTable.query.filter_by(username="john").first()
admin_role = RoleTable.query.filter_by(name="Admin").first()

# Add Admin role
user.roles.append(admin_role)
db.session.commit()

# Remove role
user.roles.remove(user_role)
db.session.commit()

# Clear all roles
user.roles.clear()
db.session.commit()
```

---

## Login Process - Complete Example

### 1. Login Form (HTML)

```html
<form method="POST" action="{{ url_for('auth.login') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    
    <div class="form-group">
        <label>Username</label>
        <input type="text" name="username" required>
    </div>
    
    <div class="form-group">
        <label>Password</label>
        <input type="password" name="password" required>
    </div>
    
    <button type="submit">Log In</button>
</form>
```

### 2. Login View (Python)

```python
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user
from app.models.user import UserTable

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        # Find user
        user = UserTable.query.filter_by(username=username).first()
        
        # Validate credentials
        if not user or not user.check_password(password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("auth.login"))
        
        # Check if active
        if not user.is_active:
            flash("Your account is inactive.", "warning")
            return redirect(url_for("auth.login"))
        
        # Create session
        login_user(user)
        flash(f"Welcome back, {user.full_name}!", "success")
        
        # Redirect by role
        if user.has_role("Admin"):
            return redirect(url_for("admin.dashboard"))
        elif user.has_role("Expert"):
            return redirect(url_for("expert.dashboard"))
        else:
            return redirect(url_for("user.dashboard"))
    
    return render_template("auth/login.html")
```

---

## Custom Decorators

### 1. Admin Required Decorator

```python
from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, flash

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        
        if not current_user.has_role("Admin"):
            flash("You don't have permission to access this page.", "danger")
            return redirect(url_for("user.dashboard"))
        
        return f(*args, **kwargs)
    
    return decorated_function
```

### 2. Expert Required Decorator

```python
def expert_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first.", "warning")
            return redirect(url_for("auth.login"))
        
        if not current_user.has_role("Expert"):
            flash("You don't have permission to access this page.", "danger")
            return redirect(url_for("user.dashboard"))
        
        return f(*args, **kwargs)
    
    return decorated_function
```

### 3. Permission Required Decorator

```python
def permission_required(permission_code):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in first.", "warning")
                return redirect(url_for("auth.login"))
            
            if not current_user.has_permission(permission_code):
                flash("You don't have the required permission.", "danger")
                return redirect(url_for("user.dashboard"))
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

# Usage:
@app.route("/admin/users")
@permission_required("manage_users")
def manage_users():
    return render_template("admin/users.html")
```

---

## Error Handling

### 1. Handle Login Errors

```python
def safe_login():
    try:
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("auth.login"))
        
        user = UserTable.query.filter_by(username=username).first()
        
        if not user:
            flash("Username not found.", "danger")
            return redirect(url_for("auth.login"))
        
        if not user.check_password(password):
            flash("Incorrect password.", "danger")
            return redirect(url_for("auth.login"))
        
        if not user.is_active:
            flash("Account is inactive.", "warning")
            return redirect(url_for("auth.login"))
        
        login_user(user)
        
        # Redirect based on role
        if user.has_role("Admin"):
            return redirect(url_for("admin.dashboard"))
        elif user.has_role("Expert"):
            return redirect(url_for("expert.dashboard"))
        else:
            return redirect(url_for("user.dashboard"))
    
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for("auth.login"))
```

### 2. Handle Access Denied

```python
@app.errorhandler(403)
def forbidden(error):
    flash("You don't have permission to access this page.", "danger")
    if current_user.is_authenticated:
        if current_user.has_role("Admin"):
            return redirect(url_for("admin.dashboard"))
        elif current_user.has_role("Expert"):
            return redirect(url_for("expert.dashboard"))
        else:
            return redirect(url_for("user.dashboard"))
    else:
        return redirect(url_for("auth.login"))
```

---

## Testing Examples

### 1. Test Login with Correct Credentials

```python
def test_login_admin():
    """Test login with admin credentials"""
    response = client.post('/auth/login', data={
        'username': 'admin_user',
        'password': 'password123'
    })
    
    assert response.status_code == 302  # Redirect
    assert '/admin/dashboard' in response.location
```

### 2. Test Login with Invalid Credentials

```python
def test_login_invalid():
    """Test login with invalid credentials"""
    response = client.post('/auth/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 302
    assert '/auth/login' in response.location
```

### 3. Test Role-Based Access

```python
def test_admin_access():
    """Test that only admin can access admin dashboard"""
    # Login as regular user
    client.post('/auth/login', data={
        'username': 'regular_user',
        'password': 'password123'
    })
    
    # Try to access admin page
    response = client.get('/admin/dashboard')
    
    # Should be redirected
    assert response.status_code == 302
    assert '/user/dashboard' in response.location
```

---

## Best Practices

✅ **Do:**
- Always use `@login_required` for authenticated routes
- Use role decorators for role-specific pages
- Hash passwords with `user.set_password()`
- Check account active status before login
- Use Flask-Login for session management
- Validate user input on both client and server
- Use CSRF tokens on all forms
- Log failed login attempts (optional)

❌ **Don't:**
- Store plain text passwords
- Assume user roles without checking
- Skip CSRF protection
- Trust client-side validation alone
- Share sensitive data in error messages
- Allow direct user_id manipulation in URLs
- Cache user data without expiration
- Hardcode redirect URLs

---

**Version:** 1.0
**Last Updated:** January 17, 2026
