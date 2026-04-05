"""
Permission-Role Service Module
Handles the complete workflow of managing permissions and their relationships with roles.
"""

from typing import List, Optional
from app.models.permission import PermissionTable
from app.models.role import RoleTable
from extensions import db


class PermissionRoleService:
    """Service for managing Permission-Role relationships and workflows."""

    # ===================== PERMISSION ASSIGNMENT =====================
    
    @staticmethod
    def assign_permission_to_role(
        permission: PermissionTable, 
        role: RoleTable
    ) -> bool:
        """
        Assign a single permission to a role.
        
        Args:
            permission: PermissionTable instance
            role: RoleTable instance
            
        Returns:
            bool: True if successful, False if already assigned
        """
        if permission in role.permissions:
            return False  # Already assigned
        
        role.permissions.append(permission)
        db.session.commit()
        return True
    
    @staticmethod
    def remove_permission_from_role(
        permission: PermissionTable,
        role: RoleTable
    ) -> bool:
        """
        Remove a permission from a role.
        
        Args:
            permission: PermissionTable instance
            role: RoleTable instance
            
        Returns:
            bool: True if removed, False if not assigned
        """
        if permission not in role.permissions:
            return False
        
        role.permissions.remove(permission)
        db.session.commit()
        return True
    
    # ===================== BULK OPERATIONS =====================
    
    @staticmethod
    def assign_multiple_permissions_to_role(
        role: RoleTable,
        permission_ids: List[int]
    ) -> dict:
        """
        Assign multiple permissions to a role at once.
        
        Args:
            role: RoleTable instance
            permission_ids: List of permission IDs
            
        Returns:
            dict: {
                'assigned': count of newly assigned,
                'skipped': count already assigned,
                'errors': list of error messages
            }
        """
        result = {
            'assigned': 0,
            'skipped': 0,
            'errors': []
        }
        
        if not permission_ids:
            return result
        
        try:
            permissions = db.session.query(PermissionTable)\
                .filter(PermissionTable.id.in_(permission_ids))\
                .all()
            
            for perm in permissions:
                if perm not in role.permissions:
                    role.permissions.append(perm)
                    result['assigned'] += 1
                else:
                    result['skipped'] += 1
            
            db.session.commit()
        except Exception as e:
            result['errors'].append(str(e))
            db.session.rollback()
        
        return result
    
    @staticmethod
    def remove_multiple_permissions_from_role(
        role: RoleTable,
        permission_ids: List[int]
    ) -> dict:
        """
        Remove multiple permissions from a role.
        
        Args:
            role: RoleTable instance
            permission_ids: List of permission IDs
            
        Returns:
            dict: {
                'removed': count removed,
                'skipped': count not assigned,
                'errors': list of error messages
            }
        """
        result = {
            'removed': 0,
            'skipped': 0,
            'errors': []
        }
        
        if not permission_ids:
            return result
        
        try:
            permissions = db.session.query(PermissionTable)\
                .filter(PermissionTable.id.in_(permission_ids))\
                .all()
            
            for perm in permissions:
                if perm in role.permissions:
                    role.permissions.remove(perm)
                    result['removed'] += 1
                else:
                    result['skipped'] += 1
            
            db.session.commit()
        except Exception as e:
            result['errors'].append(str(e))
            db.session.rollback()
        
        return result
    
    @staticmethod
    def replace_role_permissions(
        role: RoleTable,
        permission_ids: List[int]
    ) -> dict:
        """
        Replace all permissions of a role with new permissions.
        
        Args:
            role: RoleTable instance
            permission_ids: List of new permission IDs
            
        Returns:
            dict with operation results
        """
        result = {
            'previous_count': len(role.permissions),
            'new_count': 0,
            'errors': []
        }
        
        try:
            if permission_ids:
                permissions = db.session.query(PermissionTable)\
                    .filter(PermissionTable.id.in_(permission_ids))\
                    .all()
                role.permissions = permissions
                result['new_count'] = len(permissions)
            else:
                role.permissions = []
            
            db.session.commit()
        except Exception as e:
            result['errors'].append(str(e))
            db.session.rollback()
        
        return result
    
    # ===================== QUERY/RETRIEVE OPERATIONS =====================
    
    @staticmethod
    def get_permission_roles(permission: PermissionTable) -> List[RoleTable]:
        """
        Get all roles that have a specific permission.
        
        Args:
            permission: PermissionTable instance
            
        Returns:
            List of RoleTable instances
        """
        return db.session.query(RoleTable)\
            .filter(RoleTable.permissions.contains(permission))\
            .all()
    
    @staticmethod
    def get_role_permissions(role: RoleTable) -> List[PermissionTable]:
        """
        Get all permissions assigned to a role.
        
        Args:
            role: RoleTable instance
            
        Returns:
            List of PermissionTable instances
        """
        return db.session.query(PermissionTable)\
            .filter(PermissionTable.roles.contains(role))\
            .order_by(PermissionTable.code)\
            .all()
    
    @staticmethod
    def get_permissions_by_module_for_role(
        role: RoleTable
    ) -> dict:
        """
        Get role permissions grouped by module.
        
        Args:
            role: RoleTable instance
            
        Returns:
            dict: {module_name: [permissions]}
        """
        from collections import defaultdict
        permissions = PermissionRoleService.get_role_permissions(role)
        
        grouped = defaultdict(list)
        for perm in permissions:
            module = perm.module or "General"
            grouped[module].append(perm)
        
        return dict(grouped)
    
    @staticmethod
    def get_unassigned_permissions(role: RoleTable) -> List[PermissionTable]:
        """
        Get permissions that are NOT assigned to a role.
        
        Args:
            role: RoleTable instance
            
        Returns:
            List of PermissionTable instances
        """
        return db.session.query(PermissionTable)\
            .filter(~PermissionTable.roles.contains(role))\
            .order_by(PermissionTable.code)\
            .all()
    
    # ===================== PERMISSION CHECK OPERATIONS =====================
    
    @staticmethod
    def has_permission(role: RoleTable, permission_code: str) -> bool:
        """
        Check if a role has a specific permission by code.
        
        Args:
            role: RoleTable instance
            permission_code: Permission code string (e.g., 'user.create')
            
        Returns:
            bool: True if role has permission
        """
        return db.session.query(PermissionTable)\
            .filter(
                PermissionTable.code == permission_code,
                PermissionTable.roles.contains(role)
            ).first() is not None
    
    @staticmethod
    def has_any_permission(role: RoleTable, permission_codes: List[str]) -> bool:
        """
        Check if a role has at least one permission from a list.
        
        Args:
            role: RoleTable instance
            permission_codes: List of permission code strings
            
        Returns:
            bool: True if role has at least one permission
        """
        return db.session.query(PermissionTable)\
            .filter(
                PermissionTable.code.in_(permission_codes),
                PermissionTable.roles.contains(role)
            ).first() is not None
    
    @staticmethod
    def has_all_permissions(role: RoleTable, permission_codes: List[str]) -> bool:
        """
        Check if a role has all permissions from a list.
        
        Args:
            role: RoleTable instance
            permission_codes: List of permission code strings
            
        Returns:
            bool: True if role has all permissions
        """
        count = db.session.query(PermissionTable)\
            .filter(
                PermissionTable.code.in_(permission_codes),
                PermissionTable.roles.contains(role)
            ).count()
        
        return count == len(permission_codes)
    
    # ===================== STATISTICS & ANALYTICS =====================
    
    @staticmethod
    def get_permission_stats(permission: PermissionTable) -> dict:
        """
        Get statistics for a permission (how many roles have it, etc).
        
        Args:
            permission: PermissionTable instance
            
        Returns:
            dict with statistics
        """
        roles_count = db.session.query(RoleTable)\
            .filter(RoleTable.permissions.contains(permission))\
            .count()
        
        return {
            'permission_id': permission.id,
            'permission_code': permission.code,
            'permission_name': permission.name,
            'roles_count': roles_count,
            'module': permission.module,
        }
    
    @staticmethod
    def get_role_stats(role: RoleTable) -> dict:
        """
        Get statistics for a role (permission count, etc).
        
        Args:
            role: RoleTable instance
            
        Returns:
            dict with statistics
        """
        permissions = PermissionRoleService.get_role_permissions(role)
        permissions_by_module = PermissionRoleService.get_permissions_by_module_for_role(role)
        
        return {
            'role_id': role.id,
            'role_name': role.name,
            'total_permissions': len(permissions),
            'permissions_by_module': {
                module: len(perms) for module, perms in permissions_by_module.items()
            },
            'modules': list(permissions_by_module.keys()),
        }
    
    @staticmethod
    def get_permission_usage_report() -> dict:
        """
        Get a usage report for all permissions (which roles use each).
        
        Returns:
            dict: {permission_code: {count, roles: [role_names]}}
        """
        permissions = db.session.query(PermissionTable).all()
        report = {}
        
        for perm in permissions:
            roles = PermissionRoleService.get_permission_roles(perm)
            report[perm.code] = {
                'id': perm.id,
                'name': perm.name,
                'count': len(roles),
                'roles': [r.name for r in roles],
                'module': perm.module,
            }
        
        return report
    
    # ===================== VALIDATION OPERATIONS =====================
    
    @staticmethod
    def validate_permission_exists(permission_id: int) -> bool:
        """
        Check if a permission exists by ID.
        
        Args:
            permission_id: Permission ID
            
        Returns:
            bool: True if exists
        """
        return db.session.query(PermissionTable)\
            .filter(PermissionTable.id == permission_id).first() is not None
    
    @staticmethod
    def validate_role_exists(role_id: int) -> bool:
        """
        Check if a role exists by ID.
        
        Args:
            role_id: Role ID
            
        Returns:
            bool: True if exists
        """
        return db.session.query(RoleTable)\
            .filter(RoleTable.id == role_id).first() is not None
    
    @staticmethod
    def validate_permission_role_assignment(
        permission_id: int,
        role_id: int
    ) -> dict:
        """
        Validate if permission can be assigned to role.
        
        Args:
            permission_id: Permission ID
            role_id: Role ID
            
        Returns:
            dict: {valid: bool, message: str}
        """
        if not PermissionRoleService.validate_permission_exists(permission_id):
            return {'valid': False, 'message': 'Permission does not exist'}
        
        if not PermissionRoleService.validate_role_exists(role_id):
            return {'valid': False, 'message': 'Role does not exist'}
        
        perm = db.session.get(PermissionTable, permission_id)
        role = db.session.get(RoleTable, role_id)
        
        if perm in role.permissions:
            return {'valid': False, 'message': 'Permission already assigned to role'}
        
        return {'valid': True, 'message': 'Valid assignment'}
