from flask import Blueprint, render_template, request, redirect, session, current_app,url_for
from flask_login import login_required, current_user
from markupsafe import escape
import MySQLdb.cursors
upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/dataUpload', methods=['GET', 'POST'])
@login_required
def dataUpload():
    uploadMessage = ''
    with current_app.app_context():  # <-- Add this context manager
        if request.method == "POST":
            conn = current_app.config['MYSQL'].connection
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            title = request.form['title'] # not sure where to put these in the database
            description = request.form['description'] # not sure where to put these in the database
            name = request.form['name']
            company = request.form['company']
            url = request.form['url']
            thumbnailUrl = request.form['thumbnailUrl']
            version = request.form['version']
            pricing = request.form['pricing']
            platform = request.form['platform']
            category = request.form['category']
            imageUpload = request.files.get('imageUpload') # not sure where to put these in the database

            cursor.execute('SELECT * FROM Tools WHERE name = %s AND company = %s', (name, company))
            tool = cursor.fetchone()
            if tool:
                uploadMessage = "Tool already exists"
                print(uploadMessage)
            else:
                cursor.execute("INSERT INTO Tools (name, company, url, thumbnail_url, " \
                "version, pricing) Values (%s, %s, %s, %s, %s, %s)", (name, company, url, thumbnailUrl, version, pricing))
                cursor.execute("SELECT idTool FROM Tools WHERE name = %s AND company = %s",(name, company))
                toolId = cursor.fetchone()['idTool']
                cursor.execute("Select idCategory FROM Category WHERE name = %s", (category,))
                categoryId = cursor.fetchone()['idCategory']
                cursor.execute("SELECT idPlatform FROM Platform WHERE name = %s", (platform,))
                platformId = cursor.fetchone()['idPlatform']
                cursor.execute("""INSERT INTO SearchIndex (idTool, idCategory, idPlatform) 
                               Values(%s, %s, %s)""", 
                               (toolId, categoryId, platformId))
                conn.commit()
                uploadMessage = "Tool successfully uploaded."
                print(uploadMessage)
                #return redirect("dataUpload.html", uploadMessage=uploadMessage)
        return render_template('dataUpload.html', title='Upload', uploadMessage=uploadMessage)
