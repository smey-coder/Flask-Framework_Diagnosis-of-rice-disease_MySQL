# Login System - Quick Reference

## 🎯 What Has Been Implemented

A complete **role-based login system** for your Flask Rice Disease Diagnosis application with three user roles:
- **Admin** - System administration
- **Expert** - Create diagnosis rules
- **User** - Use diagnosis system

---

## 📋 Quick Start

### 1️⃣ Create Roles in Database
```sql
INSERT INTO tbl_roles (name, description) VALUES 
('Admin', 'System administrator'),
('Expert', 'Expert user'),
('User', 'Regular user');
```

### 2️⃣ Assign Roles to Users
```sql
-- Make user with id=1 an Admin
INSERT INTO tbl_user_roles (user_id, role_id) VALUES (1, 1);

-- Make user with id=2 an Expert
INSERT INTO tbl_user_roles (user_id, role_id) VALUES (2, 2);

-- Make user with id=3 a User
INSERT INTO tbl_user_roles (user_id, role_id) VALUES (3, 3);
```

### 3️⃣ Test Login
```
Username: admin_user
Password: (your password)
Expected: Redirect to /admin/dashboard

Username: expert_user
Password: (your password)
Expected: Redirect to /expert/dashboard

Username: regular_user
Password: (your password)
Expected: Redirect to /user/dashboard
```

---

## 🔄 Login Flow (30 seconds)

```
User submits login form
    ↓
Validate credentials
    ↓
Check account active
    ↓
Create session
    ↓
Check user role
    ├─ Admin? → /admin/dashboard
    ├─ Expert? → /expert/dashboard
    └─ User? → /user/dashboard
```

---

## 📂 Files Changed

| File | Change | Type |
|------|--------|------|
| `app/routes/auth_routes.py` | Added role-based redirection | Modified |
| `app/routes/admin_route/__init__.py` | Admin dashboard route | Created |
| `app/routes/expert_route/__init__.py` | Expert dashboard route | Created |
| `app/routes/user_route/__init__.py` | User dashboard route | Created |
| `app/templates/auth/login.html` | Added role badges | Modified |
| `app/templates/user_page/dashboard.html` | User dashboard template | Created |
| `app/__init__.py` | Register blueprints | Modified |

---

## 🚀 Key Routes

| Route | Method | Role | Purpose |
|-------|--------|------|---------|
| `/auth/login` | GET/POST | - | Login page |
| `/admin/dashboard` | GET | Admin | Admin panel |
| `/expert/dashboard` | GET | Expert | Expert panel |
| `/user/dashboard` | GET | User | User panel |
| `/` | GET | - | Home redirect |

---

## 🔐 Security Features

✅ Password hashing with werkzeug
✅ CSRF protection on forms
✅ Session management with Flask-Login
✅ Role-based access control
✅ Account status verification
✅ Secure cookie handling

---

## 🧪 Testing Checklist

- [ ] Create roles in database
- [ ] Create test users
- [ ] Assign roles to users
- [ ] Test login as Admin → /admin/dashboard
- [ ] Test login as Expert → /expert/dashboard
- [ ] Test login as User → /user/dashboard
- [ ] Test invalid credentials → error message
- [ ] Test unauthorized access → redirect

---

## 💻 Check User Role in Code

### Python (Views)
```python
from flask_login import current_user

if current_user.has_role("Admin"):
    # Do admin stuff
    pass
```

### HTML Templates
```html
{% if current_user.has_role("Admin") %}
    <!-- Show admin content -->
{% endif %}
```

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| `LOGIN_PROCESS_DOCUMENTATION.md` | Detailed architecture & flow |
| `SETUP_GUIDE.md` | Installation & setup steps |
| `CODE_EXAMPLES.md` | Usage examples & patterns |
| `VISUAL_GUIDE.md` | Diagrams & flowcharts |
| `IMPLEMENTATION_SUMMARY.md` | Complete summary |
| `QUICK_REFERENCE.md` | This file! |

---

## ⚡ Common Tasks

### Check if user is admin
```python
if current_user.has_role("Admin"):
    # Show admin panel
```

### Protect route for admins only
```python
@app.route("/admin")
@admin_required  # Custom decorator
def admin_page():
    return render_template("admin.html")
```

### Get user's roles
```python
roles = [role.name for role in current_user.roles]
# Returns: ["Admin", "Expert"]
```

### Get user's permissions
```python
permissions = current_user.get_permission_code()
# Returns: {"view_users", "manage_users", ...}
```

---

## 🆘 Troubleshooting

**Problem:** Login button not working
- **Solution:** Check CSRF token in form

**Problem:** Redirect loop
- **Solution:** Verify roles exist in database

**Problem:** "Permission denied" error
- **Solution:** Check user roles are assigned in tbl_user_roles

**Problem:** Session expires immediately
- **Solution:** Check Flask SECRET_KEY is set

---

## 🔗 Related Files

- User Model: `app/models/user.py`
- Role Model: `app/models/role.py`
- Auth Service: `app/services/auth_service.py`
- Base Template: `app/templates/layouts/base.html`

---

## ✨ Features

✅ Username/password login
✅ Role-based dashboard redirect
✅ Account status verification
✅ CSRF protection
✅ Password hashing
✅ Session management
✅ Custom role decorators
✅ User-friendly error messages
✅ Responsive login page

---

## 🎓 Next Steps

1. ✅ Implement login system (DONE)
2. ⏳ Customize dashboard templates
3. ⏳ Add role-based menus
4. ⏳ Implement feature permissions
5. ⏳ Add two-factor auth (optional)

---

## 📞 Need Help?

1. **Setup Issues?** → Check `SETUP_GUIDE.md`
2. **Want Code Examples?** → Check `CODE_EXAMPLES.md`
3. **Need Diagrams?** → Check `VISUAL_GUIDE.md`
4. **Full Details?** → Check `LOGIN_PROCESS_DOCUMENTATION.md`

---

**Status:** ✅ Ready for Testing
**Version:** 1.0.0
**Last Updated:** January 17, 2026
