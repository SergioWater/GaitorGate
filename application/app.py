import os
from unicodedata import category
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    UserMixin,
    current_user,
)
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb.cursors
import re
from markupsafe import escape
from flask_mail import Mail

from routes.main import main_bp
from routes.search import search_bp
from routes.auth import auth_bp
from routes.review import review_bp
from routes.upload import upload_bp
from routes.history import history_bp
from routes.favorites import favorites_bp
from routes.view_tool import view_tool_bp
from routes.chat import chat_bp

app = Flask(__name__, instance_relative_config=True)

# register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(search_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(review_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(history_bp)
app.register_blueprint(favorites_bp)
app.register_blueprint(view_tool_bp)
app.register_blueprint(chat_bp)

app.secret_key = "5e2eef1ab7c2d3eb6d3057afacea039a330acf8ab35dfdf362b0a844cda25051"

# Database connection
app.config["MYSQL_USER"] = "team3admin"
app.config["MYSQL_PASSWORD"] = "12345"
app.config["MYSQL_DB"] = "TestDb"
app.config["MYSQL_HOST"] = "18.222.76.244"

mysql = MySQL(app)
app.config["MYSQL"] = mysql

# Flask Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'auth.login' #rememme asdsaasdadaadad
bcrypt = Bcrypt(app)
app.config["BCRYPT"] = bcrypt

# Email Configuration
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True").lower() in (
    "true",
    "1",
    "t",
)
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get(
    "MAIL_DEFAULT_SENDER", "noreply@gaitorgate.com"
)  # Should match MAIL_USERNAME
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get(
    "SECURITY_PASSWORD_SALT", "email-confirm-salt"
)
mail = Mail(app)
app.config["MAIL"] = mail


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username, password, email, Account_Type):
        self.id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.Account_Type = Account_Type

    @staticmethod
    def get(user_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT username, hashed_password, email, Account_Type FROM Account WHERE idAccount = %s",
            (user_id,),
        )
        result = cursor.fetchone()
        cursor.close()
        if result:
            return User(
                user_id,
                result["username"],
                result["hashed_password"],
                result["email"],
                result["Account_Type"],
            )


# Flask-Login User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Make is_favorited function available in templates
@app.context_processor
def utility_processor():
    from routes.favorites import is_favorited

    return dict(is_favorited=is_favorited)
