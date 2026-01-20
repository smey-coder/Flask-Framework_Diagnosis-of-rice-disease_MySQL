# Login System Setup Guide

## Quick Start

### 1. Verify Implementation
All required files have been created and updated:
- ✅ Admin dashboard route (`/admin/dashboard`)
- ✅ Expert dashboard route (`/expert/dashboard`)
- ✅ User dashboard route (`/user/dashboard`)
- ✅ Role-based login redirection
- ✅ Login page with role information

### 2. Create Required Roles in Database

Run these SQL commands in your MySQL database:

```sql
-- Insert the three main roles
INSERT INTO tbl_roles (name, description) VALUES 
('Admin', 'System administrator with full access'),
('Expert', 'Expert user who creates diagnosis rules'),
('User', 'Regular user who uses the diagnosis system');
```

### 3. Assign Roles to Users

For each user, add their roles in the `tbl_user_roles` table:

```sql
-- Example: Assign Admin role to user with id 1
INSERT INTO tbl_user_roles (user_id, role_id) 
SELECT 1, id FROM tbl_roles WHERE name = 'Admin';

-- Example: Assign Expert role to user with id 2
INSERT INTO tbl_user_roles (user_id, role_id) 
SELECT 2, id FROM tbl_roles WHERE name = 'Expert';

-- Example: Assign User role to user with id 3
INSERT INTO tbl_user_roles (user_id, role_id) 
SELECT 3, id FROM tbl_roles WHERE name = 'User';
```

### 4. Test the Login System

1. Start the Flask application:
```bash
python run.py
```

2. Navigate to http://localhost:5000/auth/login

3. Test login with different user roles:
   - **Admin User** → Should redirect to `/admin/dashboard`
   - **Expert User** → Should redirect to `/expert/dashboard`
   - **Regular User** → Should redirect to `/user/dashboard`

---

## URL Routes

### Authentication Routes
- `GET/POST /auth/login` - Login page
- `GET /auth/logout` - Logout (requires login)
- `GET/POST /auth/register` - Register new account
- `GET/POST /auth/forget_password` - Password recovery
- `POST /auth/verify_reset` - Verify reset code
- `POST /auth/reset_password` - Reset password

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard (requires Admin role)
- `GET /admin/` - Redirect to admin dashboard

### Expert Routes
- `GET /expert/dashboard` - Expert dashboard (requires Expert role)
- `GET /expert/` - Redirect to expert dashboard

### User Routes
- `GET /user/dashboard` - User dashboard (requires login)
- `GET /user/` - Redirect to user dashboard

### Home
- `GET /` - Redirects based on user role or to login

---

## Login Flow

```
1. User visits /auth/login (GET)
   └─> Shows login form with role information

2. User submits username & password (POST)
   ├─> Username not found
   │   └─> Show error message, stay on login page
   │
   ├─> Password incorrect
   │   └─> Show error message, stay on login page
   │
   ├─> Account inactive
   │   └─> Show warning message, stay on login page
   │
   └─> Valid credentials
       ├─> Create session with login_user()
       ├─> Check user.has_role()
       ├─> If Admin → Redirect to /admin/dashboard
       ├─> If Expert → Redirect to /expert/dashboard
       └─> Else → Redirect to /user/dashboard
```

---

## Role-Based Access Control

### Admin Dashboard
- Protected by `@admin_required` decorator
- Only users with "Admin" role can access
- Unauthorized users redirected to user dashboard

### Expert Dashboard
- Protected by `@expert_required` decorator
- Only users with "Expert" role can access
- Unauthorized users redirected to user dashboard

### User Dashboard
- Protected by `@login_required` decorator
- Any authenticated user can access
- All roles have access (User, Expert, Admin)

---

## File Structure

```
app/
├── routes/
│   ├── auth_routes.py                    (Updated: login logic with role-based redirection)
│   ├── admin_route/
│   │   └── __init__.py                   (New: Admin dashboard routes)
│   ├── expert_route/
│   │   └── __init__.py                   (New: Expert dashboard routes)
│   └── user_route/
│       └── __init__.py                   (New: User dashboard routes)
├── templates/
│   ├── auth/
│   │   └── login.html                    (Updated: Added role information)
│   ├── admin_page/
│   │   └── dashboard.html                (Existing)
│   ├── expert_page/
│   │   └── dashboard.html                (Existing)
│   └── user_page/
│       └── dashboard.html                (New: User dashboard template)
└── __init__.py                           (Updated: Registered new blueprints)
```

---

## Database Schema

### Users Table (tbl_users)
```sql
CREATE TABLE tbl_users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    full_name VARCHAR(80) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Roles Table (tbl_roles)
```sql
CREATE TABLE tbl_roles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(80) UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### User-Role Association (tbl_user_roles)
```sql
CREATE TABLE tbl_user_roles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES tbl_users(id),
    FOREIGN KEY (role_id) REFERENCES tbl_roles(id)
);
```

---

## Security Features

✅ **Password Hashing**
- Uses werkzeug.security
- Passwords never stored in plain text

✅ **CSRF Protection**
- Flask-WTF CSRF tokens
- Applied to all POST requests

✅ **Session Management**
- Flask-Login user sessions
- Secure session cookies

✅ **Role-Based Access Control**
- Custom decorators for role checking
- Automatic redirection on unauthorized access

✅ **Account Status Verification**
- Checks if user account is active
- Prevents login for inactive accounts

---

## Troubleshooting

### Issue: "You do not have permission to access this page"
**Solution:** User doesn't have the required role. Verify role assignment in database.

### Issue: Redirect loop between login and dashboard
**Solution:** Check that `current_user.has_role()` method works correctly. Verify roles are in database.

### Issue: Login button not working
**Solution:** Ensure CSRF token is in form. Check Flask-WTF configuration.

### Issue: "Please log in to access this page"
**Solution:** User session expired or login_required decorator is blocking. Re-login.

---

## Next Steps

1. ✅ Setup roles in database
2. ✅ Assign roles to test users
3. ✅ Test login with different users
4. ⏳ Customize dashboard templates
5. ⏳ Add navigation menus based on roles
6. ⏳ Implement feature-level permissions

---

**Documentation Version:** 1.0
**Last Updated:** January 17, 2026
**Status:** ✅ Ready for Testing
