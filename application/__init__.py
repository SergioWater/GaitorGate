import os
from unicodedata import category

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

# # create and configure the app
# app.config.from_mapping(
#     SECRET_KEY="dev",
#     DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
# )

# if test_config is None:
#     # load the instance config, if it exists, when not testing
#     app.config.from_pyfile("config.py", silent=True)
# else:
#     # load the test config if passed in
#     app.config.from_mapping(test_config)

# # ensure the instance folder exists
# try:
#     os.makedirs(app.instance_path)
# except OSError:
#     pass

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
    if request.method == "POST":
        query = request.form['search'].strip() #get text entered in search bar
        category_name = request.form.get('category') # get selected category
        content_type = request.form.get('content_type') # get selected type
        published_date = request.form.get('published_date') # get selected published date
        print(
            f"Category: {category_name}, Content Type: {content_type}, Published Date: {published_date}, Search Query: {query}")


        search = """
            SELECT d.docID, d.title, d.author, d.url,d.thumbnail_url ,d.published_date, C.name AS category
            FROM SearchIndex si
            JOIN Document d ON si.document_id = d.docID
            LEFT JOIN Category C on C.categoryID = si.category_id
            LEFT JOIN Type t ON t.idType = si.type_ID
            """

        params = []
        has_filters = False

        if not any ([query, category_name, content_type, published_date]):
            print("No filters or query, executing SELECT *")
            cursor.execute(search)
        else:
            if category_name:
                search += " WHERE C.name = %s"
                params.append(category_name)
                has_filters = True

            if content_type:
                if has_filters:
                    search += " AND t.name = %s"
                else:
                    search += " WHERE t.name = %s"
                    has_filters = True
                params.append(content_type)


            if published_date:
                if has_filters:
                    search += " AND YEAR (d.published_date) = %s"
                else:
                    search += " WHERE YEAR (d.published_date) = %s"
                    has_filters = True
                params.append(published_date)


        # search by author or book
        cursor.execute(search, tuple(params))
        conn.commit()
        data = cursor.fetchall()
        # all in the search box will return all the tuples
        # if len(data) == 0 and book == 'all': 
        #     cursor.execute("SELECT name, author from Book")
        #     conn.commit()
        #     data = cursor.fetchall()
        print(*data, sep='\n')
        return render_template('index.html', data=data)
        return redirect('/')

if __name__ == '__main__':
    app.debug = True
    app.run()