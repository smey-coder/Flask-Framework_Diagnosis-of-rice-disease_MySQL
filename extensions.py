from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()
login_manager = LoginManager()
oauth = OAuth()
