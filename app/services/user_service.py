from typing import List, Optional
from app.models.user import UserTable
from app.models.role import RoleTable
from extensions import db
from app.services.audit_service import log_audit 

class UserService:

    # ---------- READ ---------- #

    @staticmethod
    def get_user_all() -> List[UserTable]:
        return UserTable.query.order_by(UserTable.id.desc()).all()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[UserTable]:
        return UserTable.query.get(user_id)

    # ---------- CREATE ---------- #

    @staticmethod
    def create_user(data: dict, password: str, role_id: Optional[int] = None) -> UserTable:
        user = UserTable(
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            is_active=data.get("is_active", True),
        )
        user.set_password(password)

        # Assign role if provided
        if role_id:
            role = db.session.get(RoleTable, role_id)
            if role:
                user.roles = [role]

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log
        log_audit(
            "CREATE",
            "users",
            user.id,
            before_data=None,
            after_data={
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "roles": [role.name for role in user.roles] if user.roles else []
            }
        )

        return user

    # ---------- UPDATE ---------- #

    @staticmethod
    def update_user(
        user: UserTable,
        data: dict,
        password: Optional[str] = None,
        role_id: Optional[int] = None
    ) -> UserTable:

        # Before snapshot
        before_data = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "roles": [role.name for role in user.roles] if user.roles else []
        }

        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.full_name = data.get("full_name", user.full_name)
        user.is_active = data.get("is_active", user.is_active)

        if password:
            user.set_password(password)

        # Update role
        if role_id is not None:
            role = db.session.get(RoleTable, role_id)
            if role:
                user.roles = [role]
            else:
                user.roles = []

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # After snapshot
        after_data = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "roles": [role.name for role in user.roles] if user.roles else []
        }

        # ✅ Audit log
        log_audit("UPDATE", "users", user.id, before_data, after_data)

        return user

    # ---------- DELETE ---------- #

    @staticmethod
    def delete_user(user: UserTable) -> None:
        # Before snapshot
        before_data = {
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "roles": [role.name for role in user.roles] if user.roles else []
        }

        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")

        # ✅ Audit log
        log_audit("DELETE", "users", user.id, before_data, after_data=None)
