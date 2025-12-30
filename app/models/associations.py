from extensions import db

tbl_user_roles = db.Table(
    "tbl_user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("tbl_users.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("tbl_roles.id"), primary_key=True),
)

tbl_role_permissions = db.Table(
    "tbl_role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("tbl_roles.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("tbl_permissions.id"), primary_key=True),
)