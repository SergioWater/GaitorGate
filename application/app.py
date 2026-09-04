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

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(search_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(review_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(history_bp)
app.register_blueprint(favorites_bp)
app.register_blueprint(view_tool_bp)
app.register_blueprint(chat_bp)

# Secrets and environment-specific configuration must come from environment variables.
required_env = [
    "FLASK_SECRET_KEY",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_DB",
    "MYSQL_HOST",
]
missing_env = [name for name in required_env if not os.environ.get(name)]
if missing_env:
    raise RuntimeError(
        "Missing required environment variables: " + ", ".join(missing_env)
    )

app.secret_key = os.environ["FLASK_SECRET_KEY"]

# Database connection
app.config["MYSQL_USER"] = os.environ["MYSQL_USER"]
app.config["MYSQL_PASSWORD"] = os.environ["MYSQL_PASSWORD"]
app.config["MYSQL_DB"] = os.environ["MYSQL_DB"]
app.config["MYSQL_HOST"] = os.environ["MYSQL_HOST"]

mysql = MySQL(app)
app.config["MYSQL"] = mysql

# Flask Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
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
)
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get(
    "SECURITY_PASSWORD_SALT", "email-confirm-salt"
)
mail = Mail(app)
app.config["MAIL"] = mail


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


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.context_processor
def utility_processor():
    from routes.favorites import is_favorited

    return dict(is_favorited=is_favorited)
