# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from flask_migrate import Migrate

migrate = Migrate(app, db)


db = SQLAlchemy()
login_manager = LoginManager()
