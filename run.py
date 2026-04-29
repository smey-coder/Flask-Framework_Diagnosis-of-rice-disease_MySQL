from app import create_app, db
from app.services.role_service import RoleService
from app.services.user_service import UserService

app = create_app()

#for Test databaes SQLLite3
# with app.app_context():
#     db.create_all()

#     UserService.seed_default_user_role()

if __name__ == "__main__":
    app.run(debug=True) 