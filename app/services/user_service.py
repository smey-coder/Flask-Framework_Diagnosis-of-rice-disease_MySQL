from typing import List, Optional

# from attr.validators import or_
from app.models.user import UserTable
from app.models.role import Role, RoleTable
from app.models.associations import tbl_user_roles
from extensions import db
from sqlalchemy import or_
from app.services.audit_service import log_audit 

class UserService:

    # ---------- READ ---------- #
    @staticmethod
    def seed_default_user_role():
        default_user_roles = [
            {
                "user_id": 2,
                "role_id": 1
            }
        ]
        for data in default_user_roles:
            # check existence using raw table
            exists = db.session.execute(
                db.select(tbl_user_roles).where(
                    (tbl_user_roles.c.user_id == data["user_id"]) &
                    (tbl_user_roles.c.role_id == data["role_id"])
                )
            ).first()
            if not exists:
                db.session.execute(
                    tbl_user_roles.insert().values(
                        user_id=data["user_id"],
                        role_id=data["role_id"]
                    )
                )

        db.session.commit()

    @staticmethod
    def get_stats():
        total = UserTable.query.count()
        active = UserTable.query.filter(UserTable.is_active.is_(True)).count()
        return {
            "total": total,
            "active": active,
            "inactive": total - active,
            "roles": db.session.query(tbl_user_roles).count(),  # your user-role association table
        }

    @staticmethod
    def get_role_names():
        return [r.name for r in RoleTable.query.order_by(RoleTable.name)]
    
    @staticmethod
    def get_user_all(page=1, per_page=10, q="", role="", status=""):
        query = UserTable.query

        if q:
            like = f"%{q}%"
            query = query.filter(or_(
                UserTable.username.ilike(like),
                UserTable.full_name.ilike(like),
                UserTable.email.ilike(like),
            ))

        if role:
            query = query.filter(UserTable.roles.any(RoleTable.name == role))

        if status == "active":
            query = query.filter(UserTable.is_active.is_(True))
        elif status == "inactive":
            query = query.filter(UserTable.is_active.is_(False))

        return query.order_by(UserTable.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
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

        # Audit log
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

        # Audit log
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

        # Audit log
        log_audit("DELETE", "users", user.id, before_data, after_data=None)
