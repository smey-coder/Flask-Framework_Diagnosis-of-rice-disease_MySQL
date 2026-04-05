"""
Permission-Role Process - Practical Usage Examples
Demonstrates real-world usage patterns for the permission-role system
"""

# ============================================================================
# EXAMPLE 1: CREATING PERMISSIONS & ROLES IN APPLICATION STARTUP
# ============================================================================

def initialize_default_permissions_and_roles():
    """
    Initialize default permissions and roles when app starts.
    This could be called from app/__init__.py or a management command.
    """
    from app.services.permission_service import PermissionService
    from app.services.role_service import RoleService
    from app.services.permission_role_service import PermissionRoleService
    from app.models.permission import PermissionTable
    from app.models.role import RoleTable
    from extensions import db
    
    # Step 1: Define all permissions
    PERMISSIONS = {
        'Users': [
            ('user.view', 'View Users', 'Can view user list and details'),
            ('user.create', 'Create User', 'Can create new user accounts'),
            ('user.edit', 'Edit User', 'Can edit user information'),
            ('user.delete', 'Delete User', 'Can delete user accounts'),
        ],
        'Roles': [
            ('role.view', 'View Roles', 'Can view role details'),
            ('role.create', 'Create Role', 'Can create new roles'),
            ('role.edit', 'Edit Role', 'Can edit role and permissions'),
            ('role.delete', 'Delete Role', 'Can delete roles'),
        ],
        'Diseases': [
            ('disease.view', 'View Diseases', 'Can view disease information'),
            ('disease.create', 'Create Disease', 'Can add new diseases'),
            ('disease.edit', 'Edit Disease', 'Can edit disease details'),
            ('disease.delete', 'Delete Disease', 'Can delete diseases'),
        ],
        'Diagnosis': [
            ('diagnosis.view', 'View Diagnosis', 'Can view diagnoses'),
            ('diagnosis.create', 'Create Diagnosis', 'Can create new diagnoses'),
            ('diagnosis.edit', 'Edit Diagnosis', 'Can edit diagnoses'),
            ('diagnosis.delete', 'Delete Diagnosis', 'Can delete diagnoses'),
        ],
        'Reports': [
            ('report.view', 'View Reports', 'Can view system reports'),
            ('report.export', 'Export Data', 'Can export data as files'),
        ],
    }
    
    # Step 2: Create permissions if not exist
    created_permissions = {}
    for module, perms in PERMISSIONS.items():
        created_permissions[module] = []
        for code, name, description in perms:
            # Check if permission already exists
            existing = db.session.scalar(
                db.select(PermissionTable).filter(PermissionTable.code == code)
            )
            if not existing:
                perm = PermissionService.create_permission({
                    'code': code,
                    'name': name,
                    'module': module,
                    'description': description,
                })
                created_permissions[module].append(perm)
            else:
                created_permissions[module].append(existing)
    
    # Step 3: Define roles with their permissions
    ROLES_CONFIG = {
        'Super Admin': {
            'description': 'Full system access - all permissions',
            'permission_codes': [code for module in PERMISSIONS.values() 
                                for code, _, _ in module],  # All permissions
        },
        'Admin': {
            'description': 'Administrative access to manage users, roles, and data',
            'permission_codes': [
                'user.view', 'user.create', 'user.edit', 'user.delete',
                'role.view', 'role.create', 'role.edit',
                'disease.view', 'disease.create', 'disease.edit',
                'diagnosis.view', 'diagnosis.create',
                'report.view', 'report.export',
            ],
        },
        'Doctor': {
            'description': 'Doctor with diagnosis and disease access',
            'permission_codes': [
                'disease.view',
                'diagnosis.view', 'diagnosis.create', 'diagnosis.edit',
                'user.view',
                'report.view',
            ],
        },
        'Manager': {
            'description': 'Manager with limited administrative access',
            'permission_codes': [
                'user.view',
                'disease.view', 'disease.create', 'disease.edit',
                'diagnosis.view', 'diagnosis.create',
                'report.view', 'report.export',
            ],
        },
        'User': {
            'description': 'Regular user with view-only permissions',
            'permission_codes': [
                'user.view',
                'disease.view',
                'diagnosis.view',
                'report.view',
            ],
        },
    }
    
    # Step 4: Create roles and assign permissions
    for role_name, config in ROLES_CONFIG.items():
        existing_role = db.session.scalar(
            db.select(RoleTable).filter(RoleTable.name == role_name)
        )
        
        if not existing_role:
            # Get permission IDs for this role
            permission_ids = []
            for module, perms in created_permissions.items():
                for perm in perms:
                    if perm.code in config['permission_codes']:
                        permission_ids.append(perm.id)
            
            # Create role with permissions
            role = RoleService.create_role(
                {
                    'name': role_name,
                    'description': config['description'],
                },
                permission_ids=permission_ids
            )
            print(f"✓ Created role: {role_name} with {len(permission_ids)} permissions")
        else:
            print(f"✓ Role '{role_name}' already exists")
    
    print("✓ Permission and role initialization complete!")


# ============================================================================
# EXAMPLE 2: ASSIGNING PERMISSIONS AT RUNTIME
# ============================================================================

def assign_permission_to_existing_role():
    """
    Example: Admin adds a new permission to an existing role
    """
    from app.services.permission_service import PermissionService
    from app.services.role_service import RoleService
    from app.services.permission_role_service import PermissionRoleService
    
    # Get the permission and role
    permission = PermissionService.get_permission_by_id(1)  # e.g., user.create
    role = RoleService.get_role_by_id(3)  # e.g., Doctor role
    
    # Assign permission to role
    if permission and role:
        success = PermissionRoleService.assign_permission_to_role(permission, role)
        
        if success:
            print(f"✓ Added '{permission.name}' to '{role.name}' role")
        else:
            print(f"! Permission already assigned to {role.name}")


def bulk_assign_permissions_to_role():
    """
    Example: Admin assigns multiple new permissions to a role at once
    """
    from app.services.role_service import RoleService
    from app.services.permission_role_service import PermissionRoleService
    
    role = RoleService.get_role_by_id(4)  # e.g., Manager role
    
    # List of permission IDs to add
    permission_ids = [1, 2, 5, 8, 12]  # IDs of permissions to assign
    
    result = PermissionRoleService.assign_multiple_permissions_to_role(
        role, 
        permission_ids
    )
    
    print(f"✓ Assignment Results:")
    print(f"  - New permissions added: {result['assigned']}")
    print(f"  - Already assigned: {result['skipped']}")
    if result['errors']:
        print(f"  - Errors: {result['errors']}")


def replace_role_permissions():
    """
    Example: Admin replaces ALL permissions of a role (for role edit form)
    """
    from app.services.role_service import RoleService
    from app.services.permission_role_service import PermissionRoleService
    
    role = RoleService.get_role_by_id(2)  # e.g., Admin role
    
    # New set of permission IDs (from form submission)
    new_permission_ids = [1, 2, 3, 4, 5, 10, 15, 20]
    
    result = PermissionRoleService.replace_role_permissions(role, new_permission_ids)
    
    print(f"✓ Role '{role.name}' permissions updated:")
    print(f"  - Previous permissions: {result['previous_count']}")
    print(f"  - New permissions: {result['new_count']}")


# ============================================================================
# EXAMPLE 3: QUERYING PERMISSIONS AND ROLES
# ============================================================================

def get_all_permissions_of_a_role():
    """
    Example: Get all permissions assigned to a specific role
    """
    from app.services.role_service import RoleService
    from app.services.permission_role_service import PermissionRoleService
    
    role = RoleService.get_role_by_id(1)
    permissions = PermissionRoleService.get_role_permissions(role)
    
    print(f"\n'{role.name}' has the following permissions:")
    for perm in permissions:
        print(f"  - [{perm.module}] {perm.code}: {perm.name}")


def get_permissions_grouped_by_module():
    """
    Example: Get permissions of a role organized by module
    """
    from app.services.role_service import RoleService
    from app.services.permission_role_service import PermissionRoleService
    
    role = RoleService.get_role_by_id(1)
    grouped = PermissionRoleService.get_permissions_by_module_for_role(role)
    
    print(f"\n'{role.name}' permissions by module:")
    for module, permissions in sorted(grouped.items()):
        print(f"\n  {module}:")
        for perm in permissions:
            print(f"    - {perm.code}: {perm.name}")


def get_which_roles_have_a_permission():
    """
    Example: Find which roles have a specific permission
    """
    from app.services.permission_service import PermissionService
    from app.services.permission_role_service import PermissionRoleService
    
    permission = PermissionService.get_permission_by_id(1)  # e.g., user.create
    roles = PermissionRoleService.get_permission_roles(permission)
    
    print(f"\nThe following roles have '{permission.code}' permission:")
    for role in roles:
        print(f"  - {role.name}")
    
    if not roles:
        print(f"  (No roles have this permission)")


def get_unassigned_permissions_for_role():
    """
    Example: Get permissions NOT assigned to a role (for "add permission" UI)
    """
    from app.services.role_service import RoleService
    from app.services.permission_role_service import PermissionRoleService
    
    role = RoleService.get_role_by_id(1)
    unassigned = PermissionRoleService.get_unassigned_permissions(role)
    
    print(f"\nPermissions NOT yet assigned to '{role.name}':")
    for perm in unassigned:
        print(f"  - [{perm.module}] {perm.code}: {perm.name}")


# ============================================================================
# EXAMPLE 4: PERMISSION CHECKING IN ROUTES
# ============================================================================

def example_route_with_permission_check():
    """
    Example: Check permissions in a Flask route
    """
    from flask import Flask, abort
    from flask_login import current_user, login_required
    from app.services.permission_role_service import PermissionRoleService
    
    app = Flask(__name__)
    
    @app.route('/users/create', methods=['GET', 'POST'])
    @login_required
    def create_user():
        """Only users with appropriate role permission can create users"""
        
        # Check if current user has 'user.create' permission
        has_permission = any(
            PermissionRoleService.has_permission(role, 'user.create')
            for role in current_user.roles
        )
        
        if not has_permission:
            abort(403)  # Forbidden
        
        # Proceed with creating user
        return "Create user form"
    
    @app.route('/roles/assign-permission/<int:role_id>', methods=['POST'])
    @login_required
    def assign_permission_to_role_route(role_id):
        """Only admins can manage role permissions"""
        
        # Check if user has admin role or 'role.edit' permission
        has_permission = any(
            PermissionRoleService.has_permission(role, 'role.edit')
            for role in current_user.roles
        )
        
        if not has_permission:
            abort(403)
        
        # Proceed with assignment logic
        return "Permission assigned"


def example_template_with_permission_check():
    """
    Example: Check permissions in Jinja2 template
    """
    template_code = """
    <!-- Show create user button only if user has permission -->
    {% if current_user.roles %}
      {% set can_create_user = current_user.roles|
         selectattr('permissions')|
         map(attribute='code')|
         select('equalto', 'user.create')|
         list %}
      
      {% if can_create_user %}
        <a href="{{ url_for('users.create') }}" class="btn btn-primary">
          Create User
        </a>
      {% endif %}
    {% endif %}
    
    <!-- Show delete button only for specific roles -->
    {% if 'Super Admin' in current_user.role_names %}
      <button class="btn btn-danger" data-action="delete">Delete</button>
    {% endif %}
    """
    return template_code


# ============================================================================
# EXAMPLE 5: REMOVING PERMISSIONS
# ============================================================================

def remove_single_permission_from_role():
    """
    Example: Remove a specific permission from a role
    """
    from app.services.permission_service import PermissionService
    from app.services.role_service import RoleService
    from app.services.permission_role_service import PermissionRoleService
    
    permission = PermissionService.get_permission_by_id(1)
    role = RoleService.get_role_by_id(2)
    
    success = PermissionRoleService.remove_permission_from_role(permission, role)
    
    if success:
        print(f"✓ Removed '{permission.name}' from '{role.name}'")
    else:
        print(f"! Permission was not assigned to {role.name}")


def remove_multiple_permissions_from_role():
    """
    Example: Remove multiple permissions from a role
    """
    from app.services.role_service import RoleService
    from app.services.permission_role_service import PermissionRoleService
    
    role = RoleService.get_role_by_id(2)
    
    # Permission IDs to remove
    permission_ids = [5, 10, 15]
    
    result = PermissionRoleService.remove_multiple_permissions_from_role(
        role,
        permission_ids
    )
    
    print(f"✓ Removal Results:")
    print(f"  - Permissions removed: {result['removed']}")
    print(f"  - Not assigned: {result['skipped']}")


# ============================================================================
# EXAMPLE 6: STATISTICS AND ANALYTICS
# ============================================================================

def get_role_statistics():
    """
    Example: Get comprehensive statistics about a role
    """
    from app.services.role_service import RoleService
    from app.services.permission_role_service import PermissionRoleService
    
    role = RoleService.get_role_by_id(1)
    stats = PermissionRoleService.get_role_stats(role)
    
    print(f"\nRole Statistics: {stats['role_name']}")
    print(f"Total Permissions: {stats['total_permissions']}")
    print(f"\nPermissions by Module:")
    for module, count in stats['permissions_by_module'].items():
        print(f"  - {module}: {count}")


def get_permission_statistics():
    """
    Example: Get statistics about a permission (which roles use it)
    """
    from app.services.permission_service import PermissionService
    from app.services.permission_role_service import PermissionRoleService
    
    permission = PermissionService.get_permission_by_id(1)
    stats = PermissionRoleService.get_permission_stats(permission)
    
    print(f"\nPermission: {stats['permission_name']} ({stats['permission_code']})")
    print(f"Module: {stats['module']}")
    print(f"Used by {stats['roles_count']} roles")


def get_permission_usage_report():
    """
    Example: Get a comprehensive report of all permissions and their usage
    """
    from app.services.permission_role_service import PermissionRoleService
    
    report = PermissionRoleService.get_permission_usage_report()
    
    print("\n=== PERMISSION USAGE REPORT ===\n")
    for code, info in sorted(report.items()):
        print(f"{info['module']:15} | {code:20} | Used by {info['count']} roles")
        if info['roles']:
            print(f"                 | {' ' * 20} | Roles: {', '.join(info['roles'])}")
        print()


# ============================================================================
# EXAMPLE 7: VALIDATION
# ============================================================================

def validate_permission_assignment():
    """
    Example: Validate before assigning a permission to a role
    """
    from app.services.permission_role_service import PermissionRoleService
    
    # Check if assignment is valid
    validation = PermissionRoleService.validate_permission_role_assignment(
        permission_id=1,
        role_id=2
    )
    
    if validation['valid']:
        print(f"✓ {validation['message']}")
        # Proceed with assignment
    else:
        print(f"✗ {validation['message']}")
        # Show error to user


# ============================================================================
# EXAMPLE 8: ADVANCED PERMISSION CHECKS
# ============================================================================

def check_multiple_permission_requirements():
    """
    Example: Check if role has multiple permission types
    """
    from app.services.role_service import RoleService
    from app.services.permission_role_service import PermissionRoleService
    
    role = RoleService.get_role_by_id(1)
    
    # Check if role has ANY of these permissions
    if PermissionRoleService.has_any_permission(
        role,
        ['user.edit', 'user.create', 'user.delete']
    ):
        print("✓ Role can perform user management")
    
    # Check if role has ALL of these permissions
    if PermissionRoleService.has_all_permissions(
        role,
        ['disease.view', 'disease.create', 'disease.edit']
    ):
        print("✓ Role has full disease management")


# ============================================================================
# EXAMPLE 9: FORM INTEGRATION (IN VIEW FUNCTIONS)
# ============================================================================

def example_form_integration():
    """
    Example: Using permission forms in Flask route
    """
    from flask import render_template, request, flash
    from app.forms.permission_forms import AssignPermissionToRoleForm
    from app.services.permission_service import PermissionService
    from app.services.permission_role_service import PermissionRoleService
    from app.models.role import RoleTable
    from extensions import db
    
    def assign_permission_view(permission_id):
        """Route to assign permission to a role"""
        permission = PermissionService.get_permission_by_id(permission_id)
        
        if not permission:
            return "Permission not found", 404
        
        form = AssignPermissionToRoleForm(permission)
        
        if form.validate_on_submit():
            role = db.session.get(RoleTable, form.role_id.data)
            
            # Assign permission
            success = PermissionRoleService.assign_permission_to_role(
                permission,
                role
            )
            
            if success:
                flash(
                    f"Permission '{permission.name}' added to '{role.name}'",
                    'success'
                )
            else:
                flash(
                    f"Permission already assigned to '{role.name}'",
                    'warning'
                )
        
        return render_template(
            'permissions/assign.html',
            permission=permission,
            form=form
        )
    
    return assign_permission_view


# ============================================================================
# EXAMPLE 10: DATA MIGRATION SCENARIO
# ============================================================================

def migrate_permissions_between_roles():
    """
    Example: Move all permissions from one role to another
    (e.g., when consolidating roles)
    """
    from app.services.role_service import RoleService
    from app.services.permission_role_service import PermissionRoleService
    
    old_role = RoleService.get_role_by_id(5)  # Old role to migrate from
    new_role = RoleService.get_role_by_id(2)  # Target role
    
    if not old_role or not new_role:
        return
    
    # Get all permissions from old role
    permissions = PermissionRoleService.get_role_permissions(old_role)
    permission_ids = [p.id for p in permissions]
    
    # Add to new role
    result = PermissionRoleService.assign_multiple_permissions_to_role(
        new_role,
        permission_ids
    )
    
    print(f"✓ Migrated {result['assigned']} permissions to '{new_role.name}'")
    print(f"  ({result['skipped']} were already assigned)")


if __name__ == "__main__":
    print("Permission-Role Process Examples")
    print("=" * 60)
    print("\nThis file contains practical usage examples.")
    print("Import specific functions in your application as needed.")
