from typing import List, Optional
from app.models.role import RoleTable
from app.models.permission import PermissionTable
from extensions import db
from sqlalchemy.orm import joinedload

class RoleService:

    @staticmethod
    def get_role_all() -> List[RoleTable]:
        return db.session.query(RoleTable)\
            .options(joinedload(RoleTable.permissions))\
            .order_by(RoleTable.id.desc())\
            .all()
    
    @staticmethod
    def get_role_by_id(role_id: int) -> Optional[RoleTable]:
        return db.session.query(RoleTable)\
            .options(joinedload(RoleTable.permissions))\
            .filter(RoleTable.id == role_id)\
            .first()
    @staticmethod
    def create_role(
        data: dict, 
        permission_ids: Optional[List[int]] = None
    ) -> RoleTable:
        role = RoleTable(
            name=data["name"],
            description=data.get("description") or "",
        )

        if permission_ids:
            perms = db.session.query(PermissionTable)\
                .filter(PermissionTable.id.in_(permission_ids))\
                .all()
            role.permissions = perms

        db.session.add(role)
        db.session.commit()
        return role

    @staticmethod
    def update_role(
        role: RoleTable, 
        data: dict, 
        permission_ids: Optional[List[int]] = None
    ) -> RoleTable:
        role.name = data["name"]
        role.description = data.get("description") or ""

        if permission_ids is not None:
            if permission_ids:
                perms = db.session.query(PermissionTable)\
                    .filter(PermissionTable.id.in_(permission_ids))\
                    .all()
                role.permissions = perms
            else:
                role.permissions = []

        db.session.commit()
        return role

    @staticmethod
    def delete_role(role: RoleTable) -> None:
        db.session.delete(role)
        db.session.commit()
