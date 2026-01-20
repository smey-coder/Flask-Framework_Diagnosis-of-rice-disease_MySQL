# Login System - Visual Guide & Diagrams

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flask Application                         │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   Route Layer                              │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │              auth_bp Blueprint                       │  │ │
│  │  │  • /auth/login (POST)   ◄──── Validates Credentials  │  │ │
│  │  │  • /auth/logout (GET)                                │  │ │
│  │  │  • /auth/register (POST)                             │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │                            │                                 │ │
│  │                            ▼                                 │ │
│  │  ┌──────────────┬──────────────┬──────────────┐             │ │
│  │  │              │              │              │             │ │
│  │  ▼              ▼              ▼              ▼             │ │
│  │  Admin      Expert            User          (Default)      │ │
│  │  │              │              │                           │ │
│  │  ▼              ▼              ▼                           │ │
│  │ ┌───┐        ┌───┐         ┌──────┐                        │ │
│  │ │ADM│        │EXP│         │USER  │                        │ │
│  │ │ BP│        │ BP│         │ BP   │                        │ │
│  │ └─┬─┘        └─┬─┘         └──┬───┘                        │ │
│  │   │            │              │                            │ │
│  └───┼────────────┼──────────────┼────────────────────────────┘ │
│      │            │              │                              │
│      ▼            ▼              ▼                              │
│   ┌─────┐      ┌─────┐       ┌────────┐                        │
│   │Admin│      │Expert│      │User    │                        │
│   │Dash │      │Dash │      │Dash    │                        │
│   └─────┘      └─────┘       └────────┘                        │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  Model Layer                               │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  UserTable                                           │  │ │
│  │  │  ├── id, username, email                            │  │ │
│  │  │  ├── password_hash, is_active                       │  │ │
│  │  │  └── roles (Many-to-Many)                           │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │           │                                                  │ │
│  │           ▼                                                  │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  RoleTable              (M2M)                        │  │ │
│  │  │  ├── Admin           tbl_user_roles                 │  │ │
│  │  │  ├── Expert          (user_id, role_id)             │  │ │
│  │  │  └── User                                           │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │                                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Template Layer                               │ │
│  │                                                             │ │
│  │  ├── auth/login.html                                      │ │
│  │  ├── admin_page/dashboard.html                           │ │
│  │  ├── expert_page/dashboard.html                          │ │
│  │  └── user_page/dashboard.html                            │ │
│  │                                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Database       │
                    │   (MySQL)        │
                    │                  │
                    │  tbl_users       │
                    │  tbl_roles       │
                    │  tbl_permissions │
                    │  tbl_user_roles  │
                    │  tbl_role_perms  │
                    └──────────────────┘
```

---

## Login Flow State Machine

```
                           ┌─────────────────┐
                           │  Not Logged In   │
                           │  (Anonymous)    │
                           └────────┬────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            /auth/login       /auth/register   (Redirected)
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                        ┌────────────────────┐
                        │   Credentials      │
                        │   Submitted        │
                        └────────┬───────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
              Valid &        Invalid    Inactive
              Active         Creds      Account
                    │            │           │
                    ▼            ▼           ▼
              ┌──────────┐  Flash   Flash
              │Create    │  Error   Warning
              │Session   │    │         │
              └────┬─────┘    │         │
                   │          ▼         ▼
                   │       /auth/login
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
    Has Admin  Has Expert  Has User
    Role       Role        Role
        │          │          │
        ▼          ▼          ▼
    /admin/    /expert/   /user/
    dashboard  dashboard  dashboard
        │          │          │
        └──────────┼──────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Logged In           │
        │  (Authenticated)     │
        └──────────┬───────────┘
                   │
           ┌───────┴───────┐
           │               │
           ▼               ▼
        /auth/logout   Other Routes
           │
           ▼
    ┌──────────────┐
    │Clear Session │
    │Flash Message │
    └──────┬───────┘
           │
           ▼
    /auth/login
           │
           └──► Not Logged In (Anonymous)
```

---

## Role Hierarchy & Permissions

```
┌─────────────────────────────────────────────────┐
│           User Role Hierarchy                   │
├─────────────────────────────────────────────────┤
│                                                 │
│   Level 3: Admin (Highest Privilege)           │
│   ├── Manage Users                             │
│   ├── Manage Roles                             │
│   ├── Manage Permissions                       │
│   ├── System Settings                          │
│   ├── View All Data                            │
│   └── Access Everything                        │
│                                                 │
│   Level 2: Expert (Medium Privilege)           │
│   ├── Create Diagnosis Rules                   │
│   ├── Manage Diseases                          │
│   ├── Manage Symptoms                          │
│   ├── View Consultations                       │
│   └── Create Expert Notes                      │
│                                                 │
│   Level 1: User (Basic Privilege)              │
│   ├── Use Diagnosis Tool                       │
│   ├── View Disease Information                 │
│   ├── View Treatments                          │
│   ├── Access Own Consultation History          │
│   └── Submit Feedback                          │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Session Management Lifecycle

```
┌──────────────┐
│ User Visits  │
│ /auth/login  │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Flask Checks:       │
│  Is User Auth?       │ ◄─── No ─── Show Login Form
└──────┬───────────────┘
       │
       Yes
       │
       ▼
┌──────────────────────┐
│ Redirect to Home     │
│ which checks role    │
└──────┬───────────────┘
       │
   ┌───┼───┬────────────┐
   │   │   │            │
   ▼   ▼   ▼            ▼
Admin Expert User    (Default)
   │    │     │
   ▼    ▼     ▼
┌─────────────────────────────────┐
│  login_user(user) creates:      │
│  • session['_user_id']          │
│  • session['_fresh']            │
│  • session['_id']               │
│  • request.user = user          │
└──────┬──────────────────────────┘
       │
       ▼
┌──────────────────────┐
│ User Authenticated   │
│ current_user set     │
└──────┬───────────────┘
       │
       ▼ (All subsequent requests)
┌──────────────────────────────┐
│ load_user() called by        │
│ Flask-Login                  │
│ from session['_user_id']     │
│ returns UserTable object     │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────┐
│ current_user =       │
│ UserTable object     │
└──────┬───────────────┘
       │
       ▼ (When user logs out)
┌──────────────────────┐
│ logout_user()        │
│ clears session       │
│ removes cookies      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ User Anonymous Again │
│ current_user = None  │
└──────┬───────────────┘
       │
       ▼
Redirect to Login
```

---

## Database Relationships

```
┌─────────────────────┐
│   tbl_users         │
├─────────────────────┤
│ id (PK)            │
│ username (UNIQUE)  │
│ email (UNIQUE)     │
│ full_name          │
│ password_hash      │
│ is_active          │
│ created_at         │
│ updated_at         │
└────────────┬────────┘
             │
    One to Many
             │
             ▼
┌──────────────────────────┐
│ tbl_user_roles (M2M)    │
├──────────────────────────┤
│ user_id (FK)            │
│ role_id (FK)            │
│ PRIMARY KEY(user_id,    │
│            role_id)     │
└────────────┬─────────────┘
             │
             ▼
┌─────────────────────┐
│   tbl_roles         │
├─────────────────────┤
│ id (PK)            │
│ name (UNIQUE)      │
│ description        │
│ created_at         │
│ updated_at         │
└────────────┬────────┘
             │
    One to Many
             │
             ▼
┌─────────────────────────────┐
│ tbl_role_permissions (M2M)  │
├─────────────────────────────┤
│ role_id (FK)               │
│ permission_id (FK)         │
│ PRIMARY KEY(role_id,       │
│            permission_id)  │
└────────────┬────────────────┘
             │
             ▼
┌──────────────────────┐
│ tbl_permissions      │
├──────────────────────┤
│ id (PK)             │
│ name                │
│ code                │
│ description         │
│ created_at          │
│ updated_at          │
└──────────────────────┘
```

---

## URL Routing Map

```
Root
│
├── /                           (Home - Role-based redirect)
│
├── /auth/                      (Authentication Blueprint)
│   ├── login         (GET/POST) ──> Login page & handler
│   ├── logout        (GET)      ──> Logout & redirect
│   ├── register      (GET/POST) ──> Registration form
│   ├── forget_password (GET/POST) ──> Password recovery
│   └── ...
│
├── /admin/                     (Admin Blueprint - @admin_required)
│   ├── dashboard     (GET)      ──> Admin dashboard
│   ├── users         (GET)      ──> Manage users
│   ├── roles         (GET)      ──> Manage roles
│   └── ...
│
├── /expert/                    (Expert Blueprint - @expert_required)
│   ├── dashboard     (GET)      ──> Expert dashboard
│   ├── rules         (GET)      ──> Create/edit rules
│   ├── diseases      (GET)      ──> Manage diseases
│   └── ...
│
├── /user/                      (User Blueprint - @login_required)
│   ├── dashboard     (GET)      ──> User dashboard
│   ├── diagnose      (GET/POST) ──> Diagnosis tool
│   └── ...
│
└── Other routes...             (Management pages, etc)
```

---

## Login Form Workflow

```
                    Browser
                       │
                       ▼
            ┌────────────────────┐
            │  GET /auth/login   │
            └──────────┬─────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  Flask renders login.html   │
        │  • Username input field      │
        │  • Password input field      │
        │  • CSRF token hidden field   │
        │  • Submit button            │
        └──────────────┬───────────────┘
                       │
                       ▼
            ┌────────────────────┐
            │ User fills form &  │
            │ submits (POST)     │
            └──────────┬─────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  POST /auth/login            │
        │  • Extract form data         │
        │  • Validate CSRF token       │
        │  • Query database            │
        │  • Check password            │
        │  • Verify is_active          │
        └──────────────┬───────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
        Fail         Fail        Success
        (No User)    (Bad Pwd)    (Valid)
          │            │            │
          ▼            ▼            ▼
        Flash        Flash       login_user()
        Error        Error       Create Session
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  302 Redirect        │
            └──────────┬───────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
   /auth/login                Dashboard
   (Error shown)              (by role)
```

---

## Access Control Decision Tree

```
                    User Requests Route
                            │
                            ▼
                ┌─────────────────────────┐
                │ Is Route Protected?     │
                └───────┬─────────────────┘
                        │
                ┌───────┴────────┐
                │                │
              No                Yes
                │                │
                ▼                ▼
            Allow         ┌──────────────┐
                         │ Is User Auth? │
                         └──┬───────┬────┘
                            │       │
                          No       Yes
                            │       │
                            ▼       ▼
                        Redirect  ┌────────────────┐
                        to Login  │ Check Role/Perm│
                                  └──┬───────┬─────┘
                                     │       │
                               No   Yes    (Granted)
                                │    │       │
                                ▼    ▼       ▼
                            Redirect Allow
                            to Default Route
                            Dashboard
```

---

## Template Render Flow

```
User Request to /admin/dashboard
        │
        ▼
    Check @login_required
        │
        ├─ Not authenticated?
        │   └─> Redirect to /auth/login
        │
        └─ Authenticated
            │
            ▼
        Check @admin_required
            │
            ├─ Not admin?
            │   └─> Redirect to /user/dashboard
            │
            └─ Is admin
                │
                ▼
            Call admin.dashboard()
                │
                ▼
            render_template('admin_page/dashboard.html',
                          user=current_user)
                │
                ▼
            Template Engine (Jinja2)
                │
                ├─ Load admin_page/dashboard.html
                ├─ Resolve template inheritance (extends)
                ├─ Process template variables
                ├─ Execute for loops, if statements
                ├─ Render HTML
                │
                ▼
            Return HTML Response
                │
                ▼
            Browser renders page
```

---

**Version:** 1.0
**Last Updated:** January 17, 2026
