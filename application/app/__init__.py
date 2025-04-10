import os
from unicodedata import category
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
#from flask_bcrypt import Bcrypt
import MySQLdb.cursors
import re
from markupsafe import escape

app = Flask(__name__, instance_relative_config=True)

app.secret_key = '5e2eef1ab7c2d3eb6d3057afacea039a330acf8ab35dfdf362b0a844cda25051'

# Database connection
app.config['MYSQL_USER'] = 'team3admin'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'TestDb'
app.config['MYSQL_HOST'] = '18.222.76.244'

mysql = MySQL(app)

# Flask Login Setup 
login_manager = LoginManager()
login_manager.init_app(app)
#login_manager.login_view = 'login'
#bcrypt = Bcrypt(app)  


RESULTS_PER_PAGE = 6

# Flask-Login User Loader
@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Account WHERE idAccount = %s", (user_id,))
    account = cursor.fetchone()
    cursor.close()
    if account:
        return User(account['idAccount'], account['username'], account['email'])
    return None

# User class for Flask-Login 
class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.id = user_id
        self.username = username
        self.email = email

    @staticmethod
    def get(user_id):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT username, email FROM Account WHERE idAccount = %s', (user_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return User(user_id, result[0], result[1])


# Home Page
@app.route("/")
def home():
    return render_template("index.html", data=[], current_page=1, total_pages=0, title='Gaitor Gate')

# About Page
@app.route("/about")
def about():
    return render_template("about.html", title='About')

# Team members
@app.route("/members/<name>")
def team_member(name):
    return render_template(f"members/{escape(name)}.html", title=name)

# Repurposed Temporarily to act as main page for new search
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html", title='Search')

@app.route('/search', methods=['GET', 'POST'])
def search():
    with app.app_context():
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        filters = request.form.getlist('filters[]')
        filter_options = request.form.getlist('filter-options[]')
        query = request.form.get('search', '').strip()
        page = request.args.get('page', 1, type=int)

        where_clauses = []
        params = []

        for i in range(len(filters)):
            selected_filter = filters[i].strip()
            filter_option = filter_options[i].strip()

            if selected_filter == 'categories' and filter_option:
                where_clauses.append("c.name = %s")
                params.append(filter_option)
            elif selected_filter == 'type' and filter_option:
                where_clauses.append("t.name = %s")
                params.append(filter_option)
            elif selected_filter == 'publishing' and filter_option:
                where_clauses.append("YEAR(d.published_date) = %s")
                params.append(filter_option)

        search_condition = """
            %s = '' OR
            MATCH(d.title) AGAINST (%s IN NATURAL LANGUAGE MODE) OR
            MATCH(k.name) AGAINST (%s IN NATURAL LANGUAGE MODE)
        """
        where_clauses.append("(" + search_condition + ")")
        params.extend([query, query, query])

        sql = """
            SELECT
                d.docID,
                d.title,
                d.author,
                d.url,
                d.thumbnail_url,
                d.published_date,
                c.name AS category
            FROM SearchIndex si
            JOIN Document d ON si.document_id = d.docID
            LEFT JOIN Category c on si.category_id = c.categoryID
            LEFT JOIN Type t ON si.type_ID = t.idType
            LEFT JOIN Keywords_Indexes ki ON ki.IndexID = si.IndexID
            LEFT JOIN Keywords k ON ki.keywordID = k.idKeywords
            WHERE {}
            GROUP BY d.title, d.docID, c.name;
        """.format(" AND ".join(where_clauses))

        cursor.execute(sql, tuple(params))
        data = cursor.fetchall()
        cursor.close()

        total_results = len(data)
        total_pages = (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        offset = (page - 1) * RESULTS_PER_PAGE
        page_data = data[offset:offset + RESULTS_PER_PAGE]

    return render_template('searchpage.html', data=page_data, current_page=page, total_pages=total_pages, title='Results')


# @app.route('/dataUpload', methods=['GET', 'POST'])
# @login_required
# def dataUpload():
#     uploadMessage = ''
#     if request.method == "POST":
#         conn = mysql.connection  # <-- Establish connection
#         cursor = conn.cursor(MySQLdb.cursors.DictCursor)
#         # add if statement and query database to make sure tool is not already in db.
#         toolName = request.form['toolName']
#         url = request.form['url']
#         # add any other attributes from form
#         cursor.execute("INSERT INTO AiTool (toolName, url) Values (%s, %s)", (toolName, url))
#         conn.commit()
#         return redirect("dataUpload.html", uploadMessage=uploadMessage)
#     return render_template('dataUpload.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    registrationMessage = ''

    with app.app_context():  # <-- Add this context manager
        conn = mysql.connection  # <-- Establish connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            cursor.execute('SELECT * FROM Account WHERE username = %s', (username,))
            account = cursor.fetchone()

            if account:
                registrationMessage = 'Account already exists!'
                print(registrationMessage)
            elif not username or not password or not email:
                registrationMessage = 'Please fill out the form!'
                print(registrationMessage)
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                registrationMessage = 'Invalid email address!'
                print(registrationMessage)
            elif not re.match(r'^[A-Za-z0-9]{4,20}$', username):
                registrationMessage = 'Username must contain only letters and numbers!'
                print(registrationMessage)
            elif password != request.form.get('confirm_password'):
                registrationMessage = 'Passwords do not match!'
                print(registrationMessage)
            else:
                # Generate the next idUser and idAccount or need to auto increment in database schema
                cursor.execute("SELECT MAX(idUser) FROM User")
                result = cursor.fetchone()
                max_user_id = list(result.values())[0] if result else 0
                new_id_user = max_user_id + 1

                cursor.execute("SELECT MAX(idAccount) FROM Account")
                result = cursor.fetchone()
                max_account_id = list(result.values())[0] if result else 0
                new_id_account = max_account_id + 1

                # 3. Insert into User since Account has foreign key to User
                test_dob = "2000-01-01"
                cursor.execute("INSERT INTO User (idUser, name, DOB) VALUES (%s, %s, %s)", 
                    (new_id_user, username, test_dob))

                # 4. Insert into Account table
                # hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                cursor.execute('''
                    INSERT INTO Account (idUser, idAccount, username, hashed_password, email)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (new_id_user, new_id_account, username, password, email))

                conn.commit()
                registrationMessage = 'You have successfully registered!'
                print(registrationMessage)

        cursor.close()

    return render_template('registration.html', registrationMessage=registrationMessage, title='Register')

@app.route('/review', methods=['GET', 'POST'])
def review():
    reviewMessage = ''

    with app.app_context():
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST' and 'username' in request.form and 'review_text' in request.form and 'rating' in request.form and 'index' in request.form:
            username = request.form['username']
            review_text = request.form['review_text']
            rating = request.form['rating']
            index = request.form['index']

            if not review_text or not rating:
                reviewMessage = 'Please fill out the form!'
                print(reviewMessage)
            elif not re.match(r'^[1-5]$', rating):
                reviewMessage = 'Rating must be between 1 and 5!'
                print(reviewMessage)
            else:
                # Generate the next idReview
                cursor.execute("SELECT idUser FROM User WHERE username = %s", (username,))
                result = cursor.fetchone()
                user_id = result['idUser'] if result else None

           
                cursor.execute("INSERT INTO Review (idUser, review_text, rating,idIndex) VALUES (%s, %s, %s,%s)",
                               (user_id, review_text, rating, index))
                conn.commit()
                reviewMessage = 'Your review has been submitted!'
                print(reviewMessage)


        cursor.close()
    return render_template('review.html', reviewMessage=reviewMessage, title='Review')



@app.route('/login', methods=['GET', 'POST'])
def login():
    loginMessage = ''
    with app.app_context():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT idAccount, username, email FROM Account WHERE username = %s AND hashed_password = %s", (username, password))
            user_data = cursor.fetchone()
            cursor.close()

            if user_data:
                user = User(user_data['idAccount'], user_data['username'], user_data['email'])
                login_user(user)
                session['username'] = user_data['username']  # Store the username in the session
                print(f"Successfully logged in as: {session['username']}")
                return redirect(url_for('account')) 
                 
            else:
                loginMessage = 'Incorrect username or password!'
                print('Incorrect username or password!')
                
    return render_template('login.html', loginMessage=loginMessage, title='Log In')

@app.route('/account')
@login_required
def account():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT username, email FROM Account WHERE idAccount = %s", (current_user.id,))
    account_info = cursor.fetchone()
    cursor.close()
    title = f"{account_info['username']}'s Account"
    return render_template('account.html', user=account_info, active_page='account', title=title)


@app.route('/logout')
@login_required
def logout():
    with app.app_context():
        session.pop('username', None) # Remove the username from the session
        logout_user()
    return redirect(url_for('login'))

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return render_template("dashboard.html")



if __name__ == '__main__':
    app.debug = True
    app.run()
