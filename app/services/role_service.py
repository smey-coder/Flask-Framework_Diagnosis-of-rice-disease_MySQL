from typing import List, Optional
from app.models.role import RoleTable
from app.models.permission import PermissionTable
from extensions import db
from sqlalchemy.orm import joinedload
from app.services.audit_service import log_audit


class RoleService:

    # ===================== READ =====================
    @staticmethod
    def get_role_all() -> List[RoleTable]:
        """Retrieve all roles with their permissions"""
        return db.session.query(RoleTable)\
            .options(joinedload(RoleTable.permissions))\
            .order_by(RoleTable.id.desc())\
            .all()
    
    @staticmethod
    def get_role_by_id(role_id: int) -> Optional[RoleTable]:
        """Retrieve a role by ID with its permissions"""
        return db.session.query(RoleTable)\
            .options(joinedload(RoleTable.permissions))\
            .filter(RoleTable.id == role_id)\
            .first()

    # ===================== CREATE =====================
    @staticmethod
    def create_role(data: dict, permission_ids: Optional[List[int]] = None) -> RoleTable:
        """Create a new role with optional permissions"""
        role = RoleTable(
            name=data["name"],
            description=data.get("description", "")
        )

        if permission_ids:
            perms = db.session.query(PermissionTable)\
                .filter(PermissionTable.id.in_(permission_ids))\
                .all()
            role.permissions = perms

        try:
            db.session.add(role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log for CREATE
        log_audit(
            "CREATE",
            "roles",
            role.id,
            before_data=None,
            after_data={
                "name": role.name,
                "description": role.description,
                "permissions": [p.name for p in role.permissions]
            }
        )

        return role

    # ===================== UPDATE =====================
    @staticmethod
    def update_role(role: RoleTable, data: dict, permission_ids: Optional[List[int]] = None) -> RoleTable:
        """Update an existing role"""

        # -------- BEFORE SNAPSHOT --------
        before_data = {
            "name": role.name,
            "description": role.description,
            "permissions": [p.name for p in role.permissions]
        }

        # -------- UPDATE FIELDS --------
        role.name = data.get("name", role.name)
        role.description = data.get("description", role.description)

        if permission_ids is not None:
            if permission_ids:
                perms = db.session.query(PermissionTable)\
                    .filter(PermissionTable.id.in_(permission_ids))\
                    .all()
                role.permissions = perms
            else:
                role.permissions = []

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # -------- AFTER SNAPSHOT --------
        after_data = {
            "name": role.name,
            "description": role.description,
            "permissions": [p.name for p in role.permissions]
        }

        # ✅ Audit log for UPDATE
        log_audit("UPDATE", "roles", role.id, before_data, after_data)

        return role

    # ===================== DELETE =====================
    @staticmethod
    def delete_role(role: RoleTable) -> None:
        """Delete a role"""

        # -------- BEFORE SNAPSHOT --------
        before_data = {
            "name": role.name,
            "description": role.description,
            "permissions": [p.name for p in role.permissions]
        }

        try:
            db.session.delete(role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log for DELETE
        log_audit("DELETE", "roles", role.id, before_data, after_data=None)
