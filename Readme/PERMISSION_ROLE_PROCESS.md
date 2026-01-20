# Permission-Role Process Workflow

## Overview

This document outlines the complete permission-role process workflow in the Flask Diagnosis System. The system uses a role-based access control (RBAC) model where:

- **Permissions** are granular access rights (e.g., "user.create", "disease.edit")
- **Roles** are collections of permissions (e.g., "Admin", "Doctor", "User")
- **Users** are assigned roles, which grant them all permissions of those roles

## Architecture

### Database Schema

```
┌─────────────────────────────────────────────────────────┐
│  Users (tbl_users)                                      │
│  - id (PK)                                              │
│  - username, email, password                            │
└──────────────────────┬──────────────────────────────────┘
                       │ (Many-to-Many)
                       │ (tbl_user_roles)
                       │
┌──────────────────────▼──────────────────────────────────┐
│  Roles (tbl_roles)                                      │
│  - id (PK)                                              │
│  - name, description                                    │
└──────────────────────┬──────────────────────────────────┘
                       │ (Many-to-Many)
                       │ (tbl_role_permissions)
                       │
┌──────────────────────▼──────────────────────────────────┐
│  Permissions (tbl_permissions)                          │
│  - id (PK)                                              │
│  - code (e.g., "user.create")                           │
│  - name (e.g., "Create User")                           │
│  - module (e.g., "Users", "Roles", "Diseases")         │
│  - description                                          │
└─────────────────────────────────────────────────────────┘
```

### Core Models

#### PermissionTable
```python
class PermissionTable(db.Model):
    id (int) - Primary Key
    code (str) - Unique permission code (e.g., "user.create")
    name (str) - Human-readable name
    module (str) - Module/feature area
    description (str) - Detailed description
    created_at, updated_at - Timestamps
    roles - Relationship (Many-to-Many)
```

#### RoleTable
```python
class RoleTable(db.Model):
    id (int) - Primary Key
    name (str) - Unique role name
    description (str) - Role description
    created_at, updated_at - Timestamps
    users - Relationship (Many-to-Many with User)
    permissions - Relationship (Many-to-Many with Permission)
```

### Association Tables

#### tbl_role_permissions
Joins roles with permissions:
- role_id (FK to tbl_roles)
- permission_id (FK to tbl_permissions)

#### tbl_user_roles
Joins users with roles:
- user_id (FK to tbl_users)
- role_id (FK to tbl_roles)

---

## Permission Management Workflow

### 1. Creating Permissions

**Form**: `PermissionCreateForm`

**Process**:
```
1. Admin fills form with:
   - Code (e.g., "user.create")
   - Name (e.g., "Create User")
   - Module (e.g., "Users")
   - Description (optional)

2. Validation:
   - Code must be unique
   - Name must be unique
   - Code format: alphanumeric + dots/hyphens

3. Service saves to database:
   - PermissionService.create_permission()
```

**Example Permissions by Module**:

| Module | Code | Name |
|--------|------|------|
| Users | user.view | View User |
| Users | user.create | Create User |
| Users | user.edit | Edit User |
| Users | user.delete | Delete User |
| Roles | role.view | View Role |
| Roles | role.create | Create Role |
| Roles | role.edit | Edit Role |
| Diseases | disease.view | View Disease |
| Diseases | disease.create | Create Disease |

### 2. Creating Roles with Initial Permissions

**Form**: `RoleCreateForm`

**Process**:
```
1. Admin creates role with:
   - Name (e.g., "Doctor")
   - Description
   - Select multiple permissions (checkboxes organized by module)

2. Validation:
   - Role name must be unique
   - At least one permission selected (optional)

3. Service saves:
   - Creates RoleTable record
   - Links permissions via tbl_role_permissions
   - RoleService.create_role(data, permission_ids)
```

### 3. Assigning Permissions to Existing Roles

**Three approaches available**:

#### A. Single Permission Assignment
**Form**: `AssignPermissionToRoleForm`

**Process**:
```
1. Admin navigates to permission detail page
2. Selects target role from dropdown
3. Service executes:
   - Validates role exists
   - Checks permission not already assigned
   - Adds permission to role
   - PermissionRoleService.assign_permission_to_role()
```

#### B. Removing Permissions from Roles
**Form**: `RemovePermissionFromRoleForm`

**Process**:
```
1. Admin on permission detail page
2. Selects role to remove from (dropdown shows roles having this permission)
3. Service executes:
   - Validates assignment exists
   - Removes permission from role
   - PermissionRoleService.remove_permission_from_role()
```

#### C. Bulk Permission Assignment
**Form**: `BulkAssignPermissionsForm`

**Process**:
```
1. Admin selects target role
2. Selects multiple permissions (checkboxes by module)
3. Service executes:
   - Validates role exists
   - Filters out already-assigned permissions
   - Adds all new permissions in one transaction
   - PermissionRoleService.assign_multiple_permissions_to_role()
```

### 4. Editing Role Permissions

**Form**: `RoleEditForm`

**Process**:
```
1. Admin edits role
2. Pre-filled checkboxes show current permissions
3. Admin selects new permission set
4. Service replaces all permissions:
   - PermissionRoleService.replace_role_permissions()
   - Removes unchecked permissions
   - Adds newly checked permissions
   - All in one transaction
```

---

## PermissionRoleService API Reference

### Assignment Operations

#### `assign_permission_to_role(permission, role) -> bool`
- Assigns single permission to role
- Returns: True if successful, False if already assigned

#### `remove_permission_from_role(permission, role) -> bool`
- Removes permission from role
- Returns: True if removed, False if not assigned

#### `assign_multiple_permissions_to_role(role, permission_ids) -> dict`
- Bulk assign multiple permissions to a role
- Returns: `{'assigned': int, 'skipped': int, 'errors': [str]}`

#### `remove_multiple_permissions_from_role(role, permission_ids) -> dict`
- Bulk remove permissions from role
- Returns: `{'removed': int, 'skipped': int, 'errors': [str]}`

#### `replace_role_permissions(role, permission_ids) -> dict`
- Replace ALL permissions of a role
- Returns: `{'previous_count': int, 'new_count': int, 'errors': [str]}`

### Query Operations

#### `get_permission_roles(permission) -> List[Role]`
Returns all roles that have a specific permission

#### `get_role_permissions(role) -> List[Permission]`
Returns all permissions assigned to a role, ordered by code

#### `get_permissions_by_module_for_role(role) -> dict`
Returns role permissions grouped by module:
```python
{
    "Users": [permission1, permission2],
    "Roles": [permission3],
    "Diseases": [permission4, permission5]
}
```

#### `get_unassigned_permissions(role) -> List[Permission]`
Returns permissions NOT assigned to a role

### Permission Check Operations

#### `has_permission(role, permission_code) -> bool`
Check if role has specific permission by code:
```python
if PermissionRoleService.has_permission(role, "user.create"):
    # Role can create users
```

#### `has_any_permission(role, permission_codes) -> bool`
Check if role has at least one permission from list

#### `has_all_permissions(role, permission_codes) -> bool`
Check if role has all permissions from list

### Statistics & Analytics

#### `get_permission_stats(permission) -> dict`
```python
{
    'permission_id': 1,
    'permission_code': 'user.create',
    'permission_name': 'Create User',
    'roles_count': 3,  # How many roles have this
    'module': 'Users'
}
```

#### `get_role_stats(role) -> dict`
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

#### `get_permission_usage_report() -> dict`
Full report of all permissions and their usage across roles

### Validation Operations

#### `validate_permission_exists(permission_id) -> bool`
#### `validate_role_exists(role_id) -> bool`
#### `validate_permission_role_assignment(permission_id, role_id) -> dict`
Validates if a permission can be assigned to a role

---

## User Permission Checking at Runtime

### In Routes/Controllers

```python
from app.services.permission_role_service import PermissionRoleService

@app.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    # Check if current user's role has permission
    user = current_user
    if not any(PermissionRoleService.has_permission(role, 'user.create') 
               for role in user.roles):
        abort(403)
    
    # Proceed with user creation
    return render_template('users/create.html')
```

### In Templates

```html
{% if current_user.roles %}
  {% set can_create_user = current_user.roles|selectattr('permissions')|map(attribute='code')|select('equalto', 'user.create')|list %}
  {% if can_create_user %}
    <a href="{{ url_for('users.create') }}" class="btn btn-primary">Create User</a>
  {% endif %}
{% endif %}
```

---

## Example Workflows

### Scenario 1: Creating a Doctor Role with Specific Permissions

```python
# Step 1: Admin creates permissions (if not exist)
disease_view = PermissionService.create_permission({
    'code': 'disease.view',
    'name': 'View Disease',
    'module': 'Diseases',
    'description': 'Can view disease details'
})

diagnosis_create = PermissionService.create_permission({
    'code': 'diagnosis.create',
    'name': 'Create Diagnosis',
    'module': 'Diagnosis',
    'description': 'Can create new diagnoses'
})

# Step 2: Admin creates role with these permissions
doctor_role = RoleService.create_role(
    data={
        'name': 'Doctor',
        'description': 'Doctor role for disease diagnosis'
    },
    permission_ids=[disease_view.id, diagnosis_create.id]
)

# Step 3: Assign user to role
# (In user service or form)
user.roles.append(doctor_role)
db.session.commit()

# Step 4: Check permissions at runtime
if PermissionRoleService.has_permission(doctor_role, 'disease.view'):
    # Show disease list
    pass
```

### Scenario 2: Adding New Permission to Multiple Roles

```python
# Step 1: Create new permission
permission = PermissionService.create_permission({
    'code': 'disease.export',
    'name': 'Export Disease Data',
    'module': 'Diseases'
})

# Step 2: Assign to multiple roles
roles_to_update = [
    RoleService.get_role_by_id(1),  # Admin
    RoleService.get_role_by_id(3),  # Manager
]

for role in roles_to_update:
    PermissionRoleService.assign_permission_to_role(permission, role)
```

### Scenario 3: Auditing Role Permissions

```python
# Get all permissions for a role
role = RoleService.get_role_by_id(1)
permissions_by_module = PermissionRoleService.get_permissions_by_module_for_role(role)

for module, permissions in permissions_by_module.items():
    print(f"\n{module}:")
    for perm in permissions:
        print(f"  - {perm.code}: {perm.name}")

# Get usage stats
stats = PermissionRoleService.get_role_stats(role)
print(f"Role: {stats['role_name']}")
print(f"Total Permissions: {stats['total_permissions']}")
print(f"Distribution by Module: {stats['permissions_by_module']}")
```

---

## Best Practices

### 1. Permission Naming Convention
```
{module}.{action}

Examples:
- user.view
- user.create
- user.edit
- user.delete
- disease.view
- disease.create
- diagnosis.view
- diagnosis.create
- role.manage
```

### 2. Module Organization
Group related permissions by feature/module:
- Users (user management)
- Roles (role management)
- Diseases (disease management)
- Diagnosis (diagnosis operations)
- Treatments (treatment management)

### 3. Role Hierarchy (Recommended)
- **Super Admin**: All permissions
- **Admin**: All permissions except system settings
- **Manager**: Department/clinic permissions
- **Doctor**: Disease diagnosis and treatment permissions
- **User**: View-only permissions

### 4. Transaction Safety
All bulk operations use db.session.commit() internally:
```python
# Safe - one transaction
result = PermissionRoleService.assign_multiple_permissions_to_role(
    role, [1, 2, 3, 4, 5]
)
```

### 5. Validation Pattern
```python
# Always validate before operations
validation = PermissionRoleService.validate_permission_role_assignment(perm_id, role_id)
if validation['valid']:
    # Proceed with assignment
    pass
else:
    # Handle error
    flash(validation['message'], 'danger')
```

---

## Forms Summary

| Form | Purpose | Module |
|------|---------|--------|
| PermissionCreateForm | Create new permission | permission_forms.py |
| PermissionEditForm | Edit existing permission | permission_forms.py |
| PermissionConfirmDeleteForm | Confirm permission deletion | permission_forms.py |
| AssignPermissionToRoleForm | Assign single permission to role | permission_forms.py |
| RemovePermissionFromRoleForm | Remove permission from role | permission_forms.py |
| BulkAssignPermissionsForm | Bulk assign multiple permissions | permission_forms.py |
| RoleCreateForm | Create role with permissions | role_forms.py |
| RoleEditForm | Edit role and its permissions | role_forms.py |

---

## Services Summary

| Service | Purpose |
|---------|---------|
| PermissionService | CRUD operations on permissions |
| RoleService | CRUD operations on roles |
| PermissionRoleService | Permission-Role relationship management |

---

## Migration & Setup

### Initial Setup
1. Create permission records for each feature
2. Create role records (Super Admin, Admin, Doctor, User)
3. Assign permissions to roles using PermissionRoleService
4. Create sample users and assign roles

### Example Data Initialization
```sql
-- Permissions
INSERT INTO tbl_permissions (code, name, module, description)
VALUES 
('user.view', 'View User', 'Users', 'Can view user details'),
('user.create', 'Create User', 'Users', 'Can create new users'),
('user.edit', 'Edit User', 'Users', 'Can edit user information'),
('user.delete', 'Delete User', 'Users', 'Can delete users'),
('role.view', 'View Role', 'Roles', 'Can view role details'),
('disease.view', 'View Disease', 'Diseases', 'Can view disease information'),
('disease.create', 'Create Disease', 'Diseases', 'Can create new diseases'),
('diagnosis.view', 'View Diagnosis', 'Diagnosis', 'Can view diagnoses'),
('diagnosis.create', 'Create Diagnosis', 'Diagnosis', 'Can create diagnoses');

-- Roles
INSERT INTO tbl_roles (name, description)
VALUES 
('Super Admin', 'Full system access'),
('Admin', 'Administrative access'),
('Doctor', 'Doctor with diagnosis permissions'),
('User', 'Regular user with view permissions');
```

---

## Troubleshooting

### Issue: Permission not showing up in role
**Solution**: Check if permission is committed to database
```python
db.session.refresh(permission)
db.session.refresh(role)
```

### Issue: Bulk operation fails partially
**Solution**: Check result dictionary for 'errors'
```python
result = PermissionRoleService.assign_multiple_permissions_to_role(role, ids)
if result['errors']:
    print(f"Errors: {result['errors']}")
    print(f"Successfully assigned: {result['assigned']}")
```

### Issue: Performance with many permissions
**Solution**: Use eager loading in queries
```python
from sqlalchemy.orm import joinedload
role = db.session.query(RoleTable)\
    .options(joinedload(RoleTable.permissions))\
    .get(role_id)
```

---

## Related Documentation
- LOGIN_PROCESS_DOCUMENTATION.md - User authentication flow
- user.py - User model with role relationships
- role.py - Role model implementation
- permission.py - Permission model implementation
