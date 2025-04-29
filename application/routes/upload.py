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
            # Get input from user
            name = request.form['name']
            company = request.form['company']
            url = request.form['url']
            thumbnailUrl = request.form['thumbnailUrl']
            version = request.form['version']
            pricing = request.form['pricing']
            platform = request.form['platform']
            category = request.form['category']
            # description = request.form['description']
            cursor.execute('SELECT * FROM Tools WHERE name = %s', (name,))
            tool_name = cursor.fetchone()
            # Check if tool already exists
            if tool_name:
                uploadMessage = "Tool already exists"
                print(uploadMessage)
            else:
                id_user = current_user.id
                print(f"USER ID: {id_user}")

                cursor.execute("INSERT INTO Company (idAccount, company_name, website) " \
                "Values(%s, %s, %s)", (id_user, company, url ))
                
                cursor.execute("SELECT idAccount FROM Company " \
                "WHERE company_name = %s AND website = %s", (company, url))
                company_id = cursor.fetchone()['idAccount']
                cursor.execute("INSERT INTO Tools (name, company, url, thumbnail_url, " \
                "version, pricing) Values (%s, %s, %s, %s, %s, %s)", 
                (name, company_id, url, thumbnailUrl, version, pricing)) # ADD DESCRIPTION ONCE FRONTEND ADDS TO FORM
                cursor.execute("SELECT idTool FROM Tools WHERE name = %s AND company = %s",(name, company_id))
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
