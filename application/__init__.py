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

    conn.commit()
    data = cursor.fetchall()

    print('Result:', *data, sep='\n')
    return render_template('index.html', data=data)
    

if __name__ == '__main__':
    app.debug = True
    app.run()