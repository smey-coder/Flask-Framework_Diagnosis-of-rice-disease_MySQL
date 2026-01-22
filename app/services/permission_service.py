from typing import List, Optional
from app.models.permission import PermissionTable
from extensions import db
from app.services.audit_service import log_audit

class PermissionService:

    # ===================== READ =====================
    @staticmethod
    def get_permission_all() -> List[PermissionTable]:
        """Retrieve all permissions"""
        return PermissionTable.query.order_by(PermissionTable.code.desc()).all()
    
    @staticmethod
    def get_permission_by_id(permission_id: int) -> Optional[PermissionTable]:
        """Retrieve permission by ID"""
        return PermissionTable.query.get(permission_id)

    # ===================== CREATE =====================
    @staticmethod
    def create_permission(data: dict) -> PermissionTable:
        """Create a new permission"""
        perm = PermissionTable(
            code=data["code"],
            name=data["name"],
            module=data.get("module", "General"),
            description=data.get("description", "")
        )

        try:
            db.session.add(perm)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log for CREATE
        log_audit(
            "CREATE",
            "permissions",
            perm.id,
            before_data=None,
            after_data={
                "code": perm.code,
                "name": perm.name,
                "module": perm.module,
                "description": perm.description
            }
        )

        return perm

    # ===================== UPDATE =====================
    @staticmethod
    def update_permission(permission: PermissionTable, data: dict) -> PermissionTable:
        """Update an existing permission"""

        # -------- BEFORE SNAPSHOT --------
        before_data = {
            "code": permission.code,
            "name": permission.name,
            "module": permission.module,
            "description": permission.description
        }

        # -------- UPDATE FIELDS --------
        permission.code = data.get("code", permission.code)
        permission.name = data.get("name", permission.name)
        permission.module = data.get("module", permission.module)
        permission.description = data.get("description", permission.description)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # -------- AFTER SNAPSHOT --------
        after_data = {
            "code": permission.code,
            "name": permission.name,
            "module": permission.module,
            "description": permission.description
        }

        # ✅ Audit log for UPDATE
        log_audit("UPDATE", "permissions", permission.id, before_data, after_data)

        return permission

    # ===================== DELETE =====================
    @staticmethod
    def delete(permission: PermissionTable) -> None:
        """Delete a permission"""

        # -------- BEFORE SNAPSHOT --------
        before_data = {
            "code": permission.code,
            "name": permission.name,
            "module": permission.module,
            "description": permission.description
        }

        try:
            db.session.delete(permission)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log for DELETE
        log_audit("DELETE", "permissions", permission.id, before_data, after_data=None)
