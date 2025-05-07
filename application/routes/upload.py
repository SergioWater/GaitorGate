from flask import Blueprint, render_template, request, redirect, session, current_app,url_for
from flask_login import login_required, current_user
from markupsafe import escape
import MySQLdb.cursors
upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/dataUpload', methods=['GET', 'POST'])
@login_required
def dataUpload():
    with current_app.app_context():  # <-- Add this context manager
        uploadMessage = ""
        if request.method == "POST":
            conn = current_app.config['MYSQL'].connection
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            # Get input from user
            name = request.form['name']
            company = current_user.id
            #companyID = current_user.id
            url = request.form['url']
            thumbnailUrl = request.form['thumbnailUrl']
            version = request.form['version']
            if not version: version = 1.0
            pricing = request.form['pricing']
            if not pricing: pricing = 0.00
            
            platform_values = [v for k, v in request.form.items() if k.startswith("platform")]
            print("Detected platforms:", platform_values)
            category = request.form['category']

            description = request.form['description']
            cursor.execute('SELECT * FROM Tools WHERE name = %s', (name,))
            tool_name = cursor.fetchone()
            # Check if tool already exists
            if tool_name:
                uploadMessage = "Tool already exists"
                print(uploadMessage)
            else:
                cursor.execute("INSERT INTO Tools (name, company, url, thumbnail_url, " \
                "version, pricing,description) Values (%s, %s, %s, %s, %s, %s,%s)", 
                (name, company, url, thumbnailUrl, version, pricing,description)) # ADD DESCRIPTION ONCE FRONTEND ADDS TO FORM
                toolId = cursor.lastrowid
                cursor.execute("Select idCategory FROM Category WHERE name = %s", (category,))
                categoryId = cursor.fetchone()['idCategory']
                
                cursor.execute("""INSERT INTO SearchIndex (idTool, idCategory) 
                               Values(%s, %s)""", 
                               (toolId, categoryId))
                conn.commit()
                indexId = cursor.lastrowid

                for platform in platform_values:
                    cursor.execute("Select idPlatform FROM Platform WHERE name = %s",(platform,))
                    platformId = cursor.fetchone()['idPlatform']
                    cursor.execute(""" INSERT INTO IndexPlatform (idIndex, idPlatform) VALUES (%s,%s)""",
                               (indexId, platformId))
                    conn.commit()

                uploadMessage = "Tool successfully uploaded."
                print(uploadMessage)
                #return redirect("dataUpload.html", uploadMessage=uploadMessage)
        return render_template('dataUpload.html', title='Upload', uploadMessage=uploadMessage)
