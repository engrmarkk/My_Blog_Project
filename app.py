# The imported classes, functions nd object from the dependencies for this project
from flask import url_for, redirect, flash
from extensions import app, db, login_manager, mail
from models import User
from routes import view, auth
import os


def create_app():
    base_dir = os.path.dirname(os.path.realpath(__file__))
    # The configuration for the URI of the database, the myblog.db is the name of this project's database
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'myblog.db')
    # The configuration for the track modification
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # The configuration to set up a secret key to strengthen the security of your database
    app.config["SECRET_KEY"] = '026b0eb800ec2934fb5cf2e7'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
    app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = True

    # Instantiate the SQLAlchemy to inherit from flask instantiation 'app'
    # Initialize the database
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # The decorator that loads the user using the user's id
    @login_manager.user_loader
    def user_loader(id):
        return User.query.get(int(id))

    # If the user isn't logged in and tries to access a login required route, this decorator allows the page to
    # redirect page to the homepage
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        flash('Login to access this page', category='info')
        return redirect(url_for('auth.login'))

    with app.app_context():
        db.create_all()

    # Register the blueprint
    app.register_blueprint(auth)
    app.register_blueprint(view)

    return app
