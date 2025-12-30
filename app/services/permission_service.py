from typing import List, Optional
from app.models.permission import PermissionTable
from extensions import db

class PermissionService:
    @staticmethod
    def get_permission_all() -> List[PermissionTable]:
        return PermissionTable.query.order_by(PermissionTable.code.desc()).all()
    
    @staticmethod
    def get_permission_by_id(permission_id: int) -> Optional[PermissionTable]:
        return PermissionTable.query.get(permission_id)
    
    @staticmethod
    def create_permission(data: dict) -> PermissionTable:
        perm = PermissionTable(
          code=data["code"],
          name=data["name"],
          module=data.get("module", "General"),
          description= data.get("description") or "",
        )
        db.session.add(perm)
        db.session.commit()
        return perm
    
    @staticmethod
    def update_permission(permission: PermissionTable, data: dict) -> PermissionTable:
        permission.code = data["code"]
        permission.name = data["name"]
        permission.module= data.get("description") or ""
        
        db.session.commit()
        return permission
    
    @staticmethod
    def delete(permission: PermissionTable) -> None:
        db.session.delete(permission)
        db.session.commit()
