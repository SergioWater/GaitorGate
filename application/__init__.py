import os
from unicodedata import category

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

from markupsafe import escape

app = Flask(__name__, instance_relative_config=True)

# Database connection
app.config['MYSQL_USER'] = 'team3admin'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'TestDb'
app.config['MYSQL_HOST'] = '18.222.76.244'

mysql = MySQL(app)


# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# About Page
@app.route("/about")
def about():
    return render_template("about.html")

# Team members
# /members/<Team member name>
@app.route("/members/<name>")
def team_member(name):
    return render_template(f"members/{escape(name)}.html")

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "GET":
        return redirect('/')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # parse form input
    selected_filter = request.form.get('filter', '').strip()
    filter_option = request.form.get('filter-options', '').strip()
    query = request.form.get('search', '').strip()

    category = filter_option if selected_filter == 'categories' else None
    res_type = filter_option if selected_filter == 'type' else None
    pub_date = filter_option if selected_filter == 'publishing' else None

    print(f"Filter Type: {selected_filter}, Filter Value: {filter_option}, Search Query: {query}")

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

        WHERE
            (%s IS NULL OR c.name = %s) AND
            (%s IS NULL OR t.name = %s) AND
            (%s IS NULL OR YEAR(d.published_date) = %s) AND
            (
                %s = '' OR
                MATCH(d.title) AGAINST (%s IN NATURAL LANGUAGE MODE) OR
                MATCH(k.name) AGAINST (%s IN NATURAL LANGUAGE MODE)
            )
        
        GROUP BY d.title, d.docID, c.name;
        """
    params = [
        category, category, 
        res_type, res_type,
        pub_date, pub_date, 
        query, query, query]

    print(sql)
    cursor.execute(sql, tuple(params))

    mysql.connection.commit()
    data = cursor.fetchall()

    print('Result:', data, sep='\n')

    cursor.close()

    return render_template('index.html', data=data)
    
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     msg = ''
#     conn = mysql.connect()  # create new connection
#     cursor = conn.cursor()
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         email = request.form['email']

#         cursor.execute('SELECT * FROM Account WHERE username = %s', (username,))
#         account = cursor.fetchone()
#         if account:
#             msg = 'Account already exists!'
#         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
#             msg = 'Invalid email address!'
#         elif not re.match(r'[A-Za-z0-9]+', username):
#             msg = 'Username must contain only letters and numbers!'
#         elif not username or not password or not email:
#             msg = 'Please fill out the form!'
#         else:
#             # Generate the next idUser and idAccount or need to auto increment in database schema
#             cursor.execute("SELECT MAX(idUser) FROM User")
#             max_user_id = cursor.fetchone()[0] or 0
#             new_id_user = max_user_id + 1

#             cursor.execute("SELECT MAX(idAccount) FROM Account")
#             max_account_id = cursor.fetchone()[0] or 0
#             new_id_account = max_account_id + 1

#             # 3. Insert into User since Account has foreign key to User
#             test_dob = "2000-01-01"  # or use a default string
#             cursor.execute("INSERT INTO User (idUser, name, DOB) VALUES (%s, %s, %s)", (new_id_user, username, test_dob))

#             # 4. Insert into Account table
#             cursor.execute('''
#                 INSERT INTO Account (idUser, idAccount, username, hashed_password, email)
#                 VALUES (%s, %s, %s, %s, %s)
#             ''', (new_id_user, new_id_account, username, password, email))

#             conn.commit()
#             msg = 'You have successfully registered!'


#     cursor.close()
#     conn.close()  
#     return render_template('registration.html', msg=msg)




if __name__ == '__main__':
    app.debug = True
    app.run()