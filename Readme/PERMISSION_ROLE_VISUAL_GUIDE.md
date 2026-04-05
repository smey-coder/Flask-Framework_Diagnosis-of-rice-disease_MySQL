# Permission-Role Process - Visual Guide

## 🏗️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     PERMISSION-ROLE SYSTEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ FRONTEND LAYER                                           │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • Permission Management Page (Create/Edit/Delete)       │  │
│  │ • Role Management Page (Create/Edit/Delete)             │  │
│  │ • Assign Permissions to Roles (Single/Bulk)             │  │
│  │ • User Management (Assign Roles to Users)               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ FORMS LAYER                                              │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • PermissionCreateForm          (Create Permission)     │  │
│  │ • PermissionEditForm            (Edit Permission)       │  │
│  │ • AssignPermissionToRoleForm   (NEW)                    │  │
│  │ • RemovePermissionFromRoleForm (NEW)                    │  │
│  │ • BulkAssignPermissionsForm    (NEW)                    │  │
│  │ • RoleCreateForm                (Create Role)           │  │
│  │ • RoleEditForm                  (Edit Role)             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ SERVICE LAYER                                            │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • PermissionService                                      │  │
│  │   - create_permission()                                  │  │
│  │   - get_permission_by_id()                               │  │
│  │   - get_permission_all()                                 │  │
│  │   - update_permission()                                  │  │
│  │   - delete()                                             │  │
│  │                                                          │  │
│  │ • RoleService                                            │  │
│  │   - create_role()                                        │  │
│  │   - get_role_by_id()                                     │  │
│  │   - get_role_all()                                       │  │
│  │   - update_role()                                        │  │
│  │   - delete_role()                                        │  │
│  │                                                          │  │
│  │ • PermissionRoleService (NEW) - 20+ Methods             │  │
│  │   - assign_permission_to_role()                          │  │
│  │   - assign_multiple_permissions_to_role()                │  │
│  │   - remove_permission_from_role()                        │  │
│  │   - get_role_permissions()                               │  │
│  │   - get_permission_roles()                               │  │
│  │   - has_permission()                                     │  │
│  │   - get_permission_usage_report()                        │  │
│  │   - ... (13+ more methods)                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ MODEL LAYER                                              │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • PermissionTable                                        │  │
│  │ • RoleTable                                              │  │
│  │ • UserTable                                              │  │
│  │ • Association Tables (tbl_role_permissions, etc)         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↓                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ DATABASE LAYER                                           │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ • tbl_permissions                                        │  │
│  │ • tbl_roles                                              │  │
│  │ • tbl_users                                              │  │
│  │ • tbl_role_permissions (Many-to-Many)                    │  │
│  │ • tbl_user_roles (Many-to-Many)                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Permission Assignment Flow

```
┌──────────────────┐
│ Admin Dashboard  │
└────────┬─────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
         ▼                                     ▼
   ┌──────────────┐                 ┌──────────────────┐
   │ Manage Perms │                 │ Manage Roles     │
   └──────┬───────┘                 └────────┬─────────┘
          │                                  │
          │  Create Permission               │  Create Role
          │  ├─ code: "user.create"         │  ├─ name: "Doctor"
          │  ├─ name: "Create User"         │  └─ description
          │  ├─ module: "Users"             │
          │  └─ description                 │
          │                                  │
          │  (Saved to tbl_permissions)      │  (Saved to tbl_roles)
          │                                  │
          └──────────────┬────────────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │  Assign Permissions        │
            │  to Roles                  │
            ├────────────────────────────┤
            │ Select Role: [Doctor ▼]    │
            │ Permissions:               │
            │ ☑ disease.view             │
            │ ☑ diagnosis.create         │
            │ ☐ user.create              │
            │ [Assign Permissions]       │
            └────────────┬───────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │  tbl_role_permissions      │
            │  role_id | perm_id         │
            │  --------|---------         │
            │    1     |   5   (disease.view)
            │    1     |   8   (diagnosis.create)
            │    2     |  10   (user.create)
            └────────────┬───────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │  User Login                │
            │  ├─ User assigned role     │
            │  └─ Inherits all perms     │
            └────────────┬───────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │  Runtime Permission Check  │
            │  if has_permission(        │
            │    role, 'disease.view')   │
            │    → Grant Access          │
            │  else                      │
            │    → Deny (403)            │
            └────────────────────────────┘
```

---

## 📊 Database Relationship Diagram

```
┌─────────────────────┐
│   tbl_users         │
├─────────────────────┤
│ id (PK)             │
│ username            │
│ email               │
│ password            │
└──────────┬──────────┘
           │
           │ (Many-to-Many)
           │ via tbl_user_roles
           │
┌──────────▼──────────┐
│  tbl_roles          │
├─────────────────────┤
│ id (PK)             │
│ name                │
│ description         │
│ created_at          │
│ updated_at          │
└──────────┬──────────┘
           │
           │ (Many-to-Many)
           │ via tbl_role_permissions
           │
┌──────────▼──────────────────┐
│  tbl_permissions            │
├─────────────────────────────┤
│ id (PK)                     │
│ code (e.g., "user.create")  │
│ name (e.g., "Create User")  │
│ module (e.g., "Users")      │
│ description                 │
│ created_at                  │
│ updated_at                  │
└─────────────────────────────┘

Association Tables:

tbl_user_roles:
┌──────────┬──────────┐
│ user_id  │ role_id  │
├──────────┼──────────┤
│    1     │    1     │ (User 1 has Admin role)
│    2     │    2     │ (User 2 has Doctor role)
│    3     │    2     │ (User 3 has Doctor role)
└──────────┴──────────┘

tbl_role_permissions:
┌──────────┬──────────────┐
│ role_id  │ permission_id│
├──────────┼──────────────┤
│    1     │      5       │ (Admin has disease.view)
│    1     │      8       │ (Admin has diagnosis.create)
│    2     │      5       │ (Doctor has disease.view)
│    2     │      8       │ (Doctor has diagnosis.create)
└──────────┴──────────────┘
```

---

## 🔍 Permission Check Workflow

```
User Requests Resource
        │
        ▼
    Is User
   Logged In?
   /       \
  No        Yes
  │         │
  ▼         ▼
Redirect   Get User
To Login   Roles
           │
           ▼
    For Each Role:
    has_permission(
      role,
      'action.code'
    )?
    /         \
   No          Yes
   │           │
   ▼           ▼
Abort 403   Proceed with
(Forbidden) Resource Access
```

---

## 📈 Service Method Hierarchy

```
PermissionRoleService
│
├─ Assignment Operations (5)
│  ├─ assign_permission_to_role()
│  ├─ remove_permission_from_role()
│  ├─ assign_multiple_permissions_to_role()
│  ├─ remove_multiple_permissions_from_role()
│  └─ replace_role_permissions()
│
├─ Query Operations (4)
│  ├─ get_permission_roles()
│  ├─ get_role_permissions()
│  ├─ get_permissions_by_module_for_role()
│  └─ get_unassigned_permissions()
│
├─ Permission Checks (3)
│  ├─ has_permission()
│  ├─ has_any_permission()
│  └─ has_all_permissions()
│
├─ Statistics (3)
│  ├─ get_permission_stats()
│  ├─ get_role_stats()
│  └─ get_permission_usage_report()
│
└─ Validation (3)
   ├─ validate_permission_exists()
   ├─ validate_role_exists()
   └─ validate_permission_role_assignment()
```

---

## 🎯 Typical Role Structure Example

```
┌──────────────────────────────────────────────────┐
│ SUPER ADMIN                                      │
├──────────────────────────────────────────────────┤
│ All Permissions:                                 │
│  ✓ Users Module: view, create, edit, delete     │
│  ✓ Roles Module: view, create, edit, delete     │
│  ✓ Diseases Module: view, create, edit, delete  │
│  ✓ Diagnosis Module: view, create, edit, delete │
│  ✓ Reports Module: view, export                 │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ ADMIN                                            │
├──────────────────────────────────────────────────┤
│ Most Permissions (no system settings):           │
│  ✓ Users: view, create, edit, delete            │
│  ✓ Roles: view, create, edit                    │
│  ✓ Diseases: view, create, edit                 │
│  ✓ Diagnosis: view, create                      │
│  ✓ Reports: view, export                        │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ DOCTOR                                           │
├──────────────────────────────────────────────────┤
│ Medical Operations:                              │
│  ✓ Diseases: view                               │
│  ✓ Diagnosis: view, create, edit                │
│  ✓ Users: view                                  │
│  ✓ Reports: view                                │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│ USER                                             │
├──────────────────────────────────────────────────┤
│ View-Only Access:                                │
│  ✓ Diseases: view                               │
│  ✓ Diagnosis: view                              │
│  ✓ Reports: view                                │
└──────────────────────────────────────────────────┘
```

---

## 🔐 Security Model

```
Layer 1: Authentication
├─ User logs in
├─ Creates session (Flask-Login)
└─ current_user available

Layer 2: Authorization
├─ Check user.roles
├─ Check role.permissions
└─ Verify required permission

Layer 3: Access Control
├─ Route level: @login_required + has_permission()
├─ Template level: {% if can_do_action %}
└─ Database level: Only load allowed data

Layer 4: Audit
├─ Track permission assignments
├─ Monitor role changes
└─ Generate usage reports

Result: Multi-layered security preventing unauthorized access
```

---

## 📊 Forms & Usage Matrix

```
┌─────────────────────────┬──────────────────┬───────────┐
│ Form Name               │ Purpose          │ Added?    │
├─────────────────────────┼──────────────────┼───────────┤
│ PermissionCreateForm    │ Create perm      │ Existing  │
│ PermissionEditForm      │ Edit perm        │ Existing  │
│ PermissionConfirmDelete │ Delete perm      │ Existing  │
│─────────────────────────┼──────────────────┼───────────┤
│ AssignPermissionToRole  │ Single assign    │ NEW ✓     │
│ RemovePermissionFromRole│ Single remove    │ NEW ✓     │
│ BulkAssignPermissions   │ Bulk assign      │ NEW ✓     │
├─────────────────────────┼──────────────────┼───────────┤
│ RoleCreateForm          │ Create role      │ Existing  │
│ RoleEditForm            │ Edit role        │ Existing  │
└─────────────────────────┴──────────────────┴───────────┘
```

---

## 🔄 Data Flow for Permission Assignment

```
Step 1: Admin selects role
   └─→ Dropdown shows all roles

Step 2: Admin selects permissions
   └─→ Checkboxes organized by module

Step 3: Admin submits form
   └─→ Form validation

Step 4: Check permission not already assigned
   └─→ Validation by form/service

Step 5: Create role_permission association
   └─→ INSERT into tbl_role_permissions

Step 6: Commit to database
   └─→ db.session.commit()

Step 7: Flash success message
   └─→ Show feedback to user

Step 8: Redirect to role detail page
   └─→ Display updated permissions
```

---

## 🎨 Component Interaction Diagram

```
┌─────────────────────────────────┐
│ User Interface Layer            │
├─────────────────────────────────┤
│ • Permission Management         │
│ • Role Management               │
│ • User Management               │
└────────────────┬────────────────┘
                 │
        ┌────────▼─────────┐
        │ Form Submission  │
        └────────┬─────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
[Perm Form] [Role Form] [Assign Form]
    │            │            │
    └────────────┼────────────┘
                 │
        ┌────────▼─────────┐
        │ Validation       │
        │ • Form level     │
        │ • Service level  │
        └────────┬─────────┘
                 │
        ┌────────▼─────────┐
        │ Service Layer    │
        │ (20+ methods)    │
        └────────┬─────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
[Perm Svc] [Role Svc] [Perm-Role Svc]
    │            │            │
    └────────────┼────────────┘
                 │
        ┌────────▼─────────┐
        │ Model Layer      │
        └────────┬─────────┘
                 │
        ┌────────▼─────────┐
        │ Database Layer   │
        │ (SQLAlchemy ORM) │
        └────────┬─────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ▼                         ▼
[MySQL] ←─────────── [Tables & Joins]
```

---

## 📋 Module Organization Chart

```
Permission Module Map:

Users
├─ user.view      → View user list and details
├─ user.create    → Create new user account
├─ user.edit      → Edit user information
└─ user.delete    → Delete user account

Roles
├─ role.view      → View role details
├─ role.create    → Create new role
├─ role.edit      → Edit role and permissions
└─ role.delete    → Delete role

Diseases
├─ disease.view   → View disease list
├─ disease.create → Add new disease
├─ disease.edit   → Edit disease info
└─ disease.delete → Delete disease

Diagnosis
├─ diagnosis.view    → View diagnosis history
├─ diagnosis.create  → Create new diagnosis
├─ diagnosis.edit    → Edit diagnosis
└─ diagnosis.delete  → Delete diagnosis

Treatments
├─ treatment.view   → View treatment info
├─ treatment.create → Add new treatment
├─ treatment.edit   → Edit treatment
└─ treatment.delete → Delete treatment

Reports
├─ report.view   → View system reports
└─ report.export → Export data as file
```

---

## 🚀 Implementation Timeline

```
Phase 1: Foundation (COMPLETE ✓)
├─ Create PermissionTable ✓
├─ Create RoleTable ✓
├─ Create association tables ✓
└─ Create basic services ✓

Phase 2: Enhanced Functionality (COMPLETE ✓)
├─ Add permission forms ✓
├─ Add role forms ✓
├─ Implement PermissionRoleService ✓
├─ Add 20+ methods ✓
└─ Add validation ✓

Phase 3: Documentation (COMPLETE ✓)
├─ Process documentation ✓
├─ API reference ✓
├─ Practical examples ✓
├─ Quick reference ✓
└─ Visual diagrams ✓

Phase 4: Integration (Ready for Implementation)
├─ Protect routes with permission checks
├─ Update templates with conditionals
├─ Initialize default permissions
├─ Create admin interface
└─ Monitor with reports
```

---

## ✅ Implementation Checklist

```
□ Read PERMISSION_ROLE_QUICK_REFERENCE.md (5 min)
□ Review PERMISSION_ROLE_PROCESS.md (15 min)
□ Study example code in PERMISSION_ROLE_EXAMPLES.py (10 min)
□ Initialize system with permissions/roles (5 min)
□ Add permission checks to key routes (15 min)
□ Update admin templates with forms (20 min)
□ Test permission assignments (10 min)
□ Setup role hierarchy (5 min)
□ Create audit report job (optional)
□ Deploy to production (30 min)

Total: ~2 hours to full implementation
```

---

## 🎓 Learning Path

```
Beginner:
1. PERMISSION_ROLE_QUICK_REFERENCE.md
2. Look at PERMISSION_ROLE_EXAMPLES.py (Example 1 & 2)
3. Use forms in admin interface

Intermediate:
1. PERMISSION_ROLE_PROCESS.md (Architecture section)
2. Review all examples
3. Implement route protection

Advanced:
1. Study complete API reference
2. Implement custom queries
3. Create audit reports
4. Optimize performance
```

---

End of Visual Guide
