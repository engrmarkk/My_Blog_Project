from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
