import os
from unicodedata import category
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb.cursors
import re
from markupsafe import escape

from .routes.main import main_bp
from .routes.search import search_bp
from .routes.auth import auth_bp

app = Flask(__name__, instance_relative_config=True)

# register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(search_bp)
app.register_blueprint(auth_bp)

app.secret_key = '5e2eef1ab7c2d3eb6d3057afacea039a330acf8ab35dfdf362b0a844cda25051'

# Database connection
app.config['MYSQL_USER'] = 'team3admin' 
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'TestDb'
app.config['MYSQL_HOST'] = '18.222.76.244'

mysql = MySQL(app)
app.config['MYSQL'] = mysql

# Flask Login Setup 
login_manager = LoginManager()
login_manager.init_app(app)
#login_manager.login_view = 'login'
bcrypt = Bcrypt(app)  
app.config['BCRYPT'] = bcrypt

# User class for Flask-Login 
class User(UserMixin):
    def __init__(self, user_id, username, password,  email):
        self.id = user_id
        self.username = username
        self.password = password
        self.email = email

    @staticmethod
    def get(user_id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT username, hashed_password, email FROM Account WHERE idAccount = %s', (user_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return User(user_id, result['username'], result['hashed_password'], result['email'])

# Flask-Login User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Repurposed Temporarily to act as main page for new search
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html", title='Search')

@app.route('/dataUpload', methods=['GET', 'POST'])
@login_required
def dataUpload():
    uploadMessage = ''
    with app.app_context():  # <-- Add this context manager
        if request.method == "POST":
            conn = mysql.connection  # <-- Establish connection
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)

            name = request.form['name']
            company = request.form['company']
            url = request.form['url']
            thumbnailUrl = request.form['thumbnail']
            version = request.form['version']
            pricing = request.form['pricing']

            cursor.execute('SELECT * FROM Tools WHERE name = %s', (name,))
            tool = cursor.fetchone()
            if tool:
                uploadMessage = "Tool already exists"
                print(uploadMessage)
            else:
                cursor.execute("INSERT INTO Tools (name, company, url, thumbnail, " \
                "version, pricing) Values (%s, %s)", (name, company, url, thumbnailUrl, version, pricing))
                conn.commit()
                print(uploadMessage)
                return redirect("dataUpload.html", uploadMessage=uploadMessage)
        return render_template('dataUpload.html')

# @app.route('/review', methods=['GET', 'POST'])
# def review():
#     reviewMessage = ''

#     with app.app_context():
#         conn = mysql.connection
#         cursor = conn.cursor(MySQLdb.cursors.DictCursor)

#         if request.method == 'POST' and 'username' in request.form and 'review_text' in request.form and 'rating' in request.form and 'index' in request.form:
#             username = request.form['username']
#             review_text = request.form['review_text']
#             rating = request.form['rating']
#             index = request.form['index']

#             if not review_text or not rating:
#                 reviewMessage = 'Please fill out the form!'
#                 print(reviewMessage)
#             elif not re.match(r'^[1-5]$', rating):
#                 reviewMessage = 'Rating must be between 1 and 5!'
#                 print(reviewMessage)
#             else:
#                 # Generate the next idReview
#                 cursor.execute("SELECT idUser FROM User WHERE username = %s", (username,))
#                 result = cursor.fetchone()
#                 user_id = result['idUser'] if result else None

           
#                 cursor.execute("INSERT INTO Review (idUser, review_text, rating,idIndex) VALUES (%s, %s, %s,%s)",
#                                (user_id, review_text, rating, index))
#                 conn.commit()
#                 reviewMessage = 'Your review has been submitted!'
#                 print(reviewMessage)


#         cursor.close()
#     return render_template('review.html', reviewMessage=reviewMessage, title='Review')

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return render_template("dashboard.html")

