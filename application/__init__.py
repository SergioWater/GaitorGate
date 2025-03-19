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

        selected_filter = request.form.get('filter', '').strip()
        filter_option = request.form.get('filter-options', '').strip()
        query = request.form.get('search', '').strip()

        print(f"Filter Type: {selected_filter}, Filter Value: {filter_option}, Search Query: {query}")

        sql = """
            SELECT d.docID, d.title, d.author, d.url,d.thumbnail_url ,d.published_date, C.name AS category
            FROM SearchIndex si
            JOIN Document d ON si.document_id = d.docID
            LEFT JOIN Category C on C.categoryID = si.category_id
            LEFT JOIN Type t ON t.idType = si.type_ID
            """

        params = []
        has_filters = False
        if not any ([query, selected_filter, filter_option]):
            print("No filters or query, executing SELECT *")
        else:
            if selected_filter == "categories" and filter_option:
                sql += "WHERE C.name = %s"
                params.append(filter_option)
                has_filters = True


            if selected_filter == "type" and filter_option:
                sql += "WHERE t.name = %s"
                params.append(filter_option)
                has_filters = True


            if selected_filter == "publishing" and filter_option:
                sql += "WHERE YEAR (d.published_date) = %s"
                params.append(filter_option)
                has_filters = True


            if query:
                if has_filters:
                    sql += " AND LOWER(d.title) LIKE LOWER(%s)"
                else:
                    sql += " WHERE LOWER(d.title) LIKE LOWER(%s)"
                params.append(f"%{query}%")

            # search by author or book

        print(sql)
        if params:
            cursor.execute(sql, tuple(params))
        else :
            cursor.execute(sql)

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