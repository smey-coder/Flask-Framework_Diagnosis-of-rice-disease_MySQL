from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_mail import Mail

db =  SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
mail = Mail()
