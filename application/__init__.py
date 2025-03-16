import os

from flask import Flask, render_template, request, redirect
from flaskext.mysql import MySQL

from markupsafe import escape

app = Flask(__name__, instance_relative_config=True)

# Database connection
app.config['MYSQL_DATABASE_USER'] = 'team3admin'
app.config['MYSQL_DATABASE_PASSWORD'] = '12345'
app.config['MYSQL_DATABASE_DB'] = 'TestDb'
app.config['MYSQL_DATABASE_HOST'] = '18.222.76.244'
mysql = MySQL()
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

# create and configure the app
app.config.from_mapping(
    SECRET_KEY="dev",
    DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
)

if test_config is None:
    # load the instance config, if it exists, when not testing
    app.config.from_pyfile("config.py", silent=True)
else:
    # load the test config if passed in
    app.config.from_mapping(test_config)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

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

# Team members
# /members/<Team member name>
@app.route("/members/<name>")
def team_member(name):
    return render_template(f"members/{escape(name)}.html")

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        book = request.form['book']
        # search by author or book
        cursor.execute("SELECT name, author from Book WHERE name LIKE %s OR author LIKE %s", (book, book))
        conn.commit()
        data = cursor.fetchall()
        # all in the search box will return all the tuples
        if len(data) == 0 and book == 'all': 
            cursor.execute("SELECT name, author from Book")
            conn.commit()
            data = cursor.fetchall()
        return render_template('search.html', data=data)
    return render_template('search.html')

if __name__ == '__main__':
    app.debug = True
    app.run()