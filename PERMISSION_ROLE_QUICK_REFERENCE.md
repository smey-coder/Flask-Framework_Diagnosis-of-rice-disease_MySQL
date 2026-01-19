# Permission-Role Process - Quick Reference Card

## 📋 Service Methods At A Glance

### Assignment (Modify Relationships)
```python
PermissionRoleService.assign_permission_to_role(permission, role) → bool
PermissionRoleService.remove_permission_from_role(permission, role) → bool
PermissionRoleService.assign_multiple_permissions_to_role(role, permission_ids) → dict
PermissionRoleService.remove_multiple_permissions_from_role(role, permission_ids) → dict
PermissionRoleService.replace_role_permissions(role, permission_ids) → dict
```

### Queries (Get Information)
```python
PermissionRoleService.get_permission_roles(permission) → List[Role]
PermissionRoleService.get_role_permissions(role) → List[Permission]
PermissionRoleService.get_permissions_by_module_for_role(role) → dict
PermissionRoleService.get_unassigned_permissions(role) → List[Permission]
```

### Checks (Permission Validation)
```python
PermissionRoleService.has_permission(role, code) → bool
PermissionRoleService.has_any_permission(role, codes) → bool
PermissionRoleService.has_all_permissions(role, codes) → bool
```

### Analytics (Statistics & Reports)
```python
PermissionRoleService.get_permission_stats(permission) → dict
PermissionRoleService.get_role_stats(role) → dict
PermissionRoleService.get_permission_usage_report() → dict
```

### Validation (Safety Checks)
```python
PermissionRoleService.validate_permission_exists(permission_id) → bool
PermissionRoleService.validate_role_exists(role_id) → bool
PermissionRoleService.validate_permission_role_assignment(perm_id, role_id) → dict
```

---

## 🎯 Common Use Cases

### Scenario 1: Check Permission in Route
```python
@app.route('/users/create')
@login_required
def create_user():
    if not any(PermissionRoleService.has_permission(r, 'user.create') for r in current_user.roles):
        abort(403)
    # ... create user
```

### Scenario 2: Assign Permission to Role
```python
perm = PermissionService.get_permission_by_id(1)
role = RoleService.get_role_by_id(2)
PermissionRoleService.assign_permission_to_role(perm, role)
```

### Scenario 3: Bulk Assign Permissions
```python
result = PermissionRoleService.assign_multiple_permissions_to_role(
    role, 
    [1, 2, 3, 4, 5]
)
print(f"Assigned: {result['assigned']}, Already had: {result['skipped']}")
```

### Scenario 4: Update Role Permissions (Replace All)
```python
result = PermissionRoleService.replace_role_permissions(
    role, 
    [10, 11, 12]  # New permission IDs
)
```

### Scenario 5: Get All Permissions of a Role
```python
permissions = PermissionRoleService.get_role_permissions(role)
for perm in permissions:
    print(f"- {perm.code}: {perm.name}")
```

### Scenario 6: Get Permissions by Module
```python
grouped = PermissionRoleService.get_permissions_by_module_for_role(role)
# Returns: {'Users': [...], 'Roles': [...], 'Diseases': [...]}
```

### Scenario 7: Find Which Roles Have a Permission
```python
roles = PermissionRoleService.get_permission_roles(permission)
for role in roles:
    print(f"Role {role.name} has this permission")
```

### Scenario 8: Get Role Statistics
```python
stats = PermissionRoleService.get_role_stats(role)
print(f"Role: {stats['role_name']}")
print(f"Permissions: {stats['total_permissions']}")
print(f"By Module: {stats['permissions_by_module']}")
```

### Scenario 9: Generate Usage Report
```python
report = PermissionRoleService.get_permission_usage_report()
for code, info in report.items():
    print(f"{code}: {info['roles']}")  # List of roles using this
```

### Scenario 10: Remove Permission from Role
```python
PermissionRoleService.remove_permission_from_role(permission, role)
```

---

## 📝 Forms Available

| Form Name | Purpose |
|-----------|---------|
| `PermissionCreateForm` | Create new permission |
| `PermissionEditForm` | Edit existing permission |
| `PermissionConfirmDeleteForm` | Confirm deletion |
| `AssignPermissionToRoleForm` | **NEW** - Assign single permission to role |
| `RemovePermissionFromRoleForm` | **NEW** - Remove permission from role |
| `BulkAssignPermissionsForm` | **NEW** - Bulk assign permissions |
| `RoleCreateForm` | Create role with permissions |
| `RoleEditForm` | Edit role and permissions |

---

## 🔍 Return Value Examples

### dict Results (Bulk Operations)
```python
{
    'assigned': 3,        # New assignments
    'skipped': 2,         # Already had these
    'errors': []          # Error messages if any
}
```

### dict Results (Statistics)
```python
{
    'role_id': 1,
    'role_name': 'Doctor',
    'total_permissions': 15,
    'permissions_by_module': {
        'Users': 4,
        'Diseases': 6,
        'Treatments': 5
    },
    'modules': ['Users', 'Diseases', 'Treatments']
}
```

### dict Results (Validation)
```python
{
    'valid': True,
    'message': 'Valid assignment'
}
```

---

## 🗂️ Database Tables Reference

```sql
-- Permissions
CREATE TABLE tbl_permissions (
    id INT PRIMARY KEY,
    code VARCHAR(64) UNIQUE,     -- e.g., 'user.create'
    name VARCHAR(120) UNIQUE,    -- e.g., 'Create User'
    description VARCHAR(255),
    module VARCHAR(80),          -- e.g., 'Users', 'Roles'
    created_at DATETIME,
    updated_at DATETIME
);

-- Roles
CREATE TABLE tbl_roles (
    id INT PRIMARY KEY,
    name VARCHAR(80) UNIQUE,
    description VARCHAR(255),
    created_at DATETIME,
    updated_at DATETIME
);

-- Role-Permission Association
CREATE TABLE tbl_role_permissions (
    role_id INT FOREIGN KEY,
    permission_id INT FOREIGN KEY,
    PRIMARY KEY (role_id, permission_id)
);

-- User-Role Association (Already exists)
CREATE TABLE tbl_user_roles (
    user_id INT FOREIGN KEY,
    role_id INT FOREIGN KEY,
    PRIMARY KEY (user_id, role_id)
);
```

---

## 🔐 Permission Code Naming Convention

```
Format: {module}.{action}

Examples:
user.view
user.create
user.edit
user.delete

role.view
role.create
role.edit
role.delete

disease.view
disease.create
disease.edit
disease.delete

diagnosis.view
diagnosis.create
diagnosis.edit
diagnosis.delete
```

---

## 📊 Role Hierarchy (Recommended)

| Role | Permissions | Use Case |
|------|-------------|----------|
| Super Admin | All | System administrator |
| Admin | Most (except system) | Administrative staff |
| Manager | Department level | Department managers |
| Doctor | Diagnosis + Disease | Medical professionals |
| User | View only | Regular users |

---

## ⚡ Quick Import

```python
from app.services.permission_role_service import PermissionRoleService
from app.services.permission_service import PermissionService
from app.services.role_service import RoleService
from app.forms.permission_forms import (
    AssignPermissionToRoleForm,
    RemovePermissionFromRoleForm,
    BulkAssignPermissionsForm
)
```

---

## 🛡️ Security Checklist

- [ ] Always check permissions in routes with `@login_required`
- [ ] Use `PermissionRoleService.has_permission()` for runtime checks
- [ ] Validate input before permission assignments
- [ ] Log permission changes for audit trail
- [ ] Regular permission audits with `get_permission_usage_report()`
- [ ] Never trust client-side permission checks alone
- [ ] Use transaction rollback on errors

---

## 🐛 Common Gotchas

1. **Refreshing Session**: After assignment, refresh objects:
   ```python
   db.session.refresh(permission)
   db.session.refresh(role)
   ```

2. **Bulk Operations**: Always check `errors` key:
   ```python
   if result['errors']:
       print(result['errors'])
   ```

3. **Multiple Conditions**: Use `has_any_permission()` or `has_all_permissions()`:
   ```python
   # This role needs EITHER permission
   if PermissionRoleService.has_any_permission(role, ['user.create', 'user.edit']):
       # ...
   ```

4. **Performance**: For many permissions, use eager loading:
   ```python
   role = db.session.query(RoleTable)\
       .options(joinedload(RoleTable.permissions))\
       .get(role_id)
   ```

---

## 📚 Documentation Files

| File | Contains |
|------|----------|
| `PERMISSION_ROLE_PROCESS.md` | Complete technical documentation |
| `PERMISSION_ROLE_EXAMPLES.py` | 10 practical code examples |
| `PERMISSION_ROLE_IMPLEMENTATION.md` | Implementation summary |
| `PERMISSION_ROLE_QUICK_REFERENCE.md` | This quick reference |

---

## 🚀 Getting Started

1. **Initialize System**:
   ```python
   from PERMISSION_ROLE_EXAMPLES import initialize_default_permissions_and_roles
   initialize_default_permissions_and_roles()
   ```

2. **Protect Routes**:
   ```python
   if not any(PermissionRoleService.has_permission(r, 'action.code') for r in current_user.roles):
       abort(403)
   ```

3. **Manage in Admin Panel**:
   - Use the forms to assign/remove permissions
   - Use service methods for bulk operations

4. **Monitor & Audit**:
   ```python
   report = PermissionRoleService.get_permission_usage_report()
   ```

---

## 💡 Pro Tips

- Use `get_unassigned_permissions()` to show available permissions in UI
- Use `get_permissions_by_module_for_role()` to display organized lists
- Combine `has_any_permission()` with `has_all_permission()` for complex rules
- Use `validate_permission_role_assignment()` before operations
- Cache role permissions for frequently accessed roles

---

## 📞 Support

Refer to:
- `PERMISSION_ROLE_PROCESS.md` → Troubleshooting section
- `PERMISSION_ROLE_EXAMPLES.py` → Real-world usage patterns
- Model files → `app/models/permission.py`, `role.py`
- Service files → `app/services/permission_role_service.py`
