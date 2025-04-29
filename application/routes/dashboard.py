from flask import Blueprint, render_template, request, redirect, session, current_app,url_for
from flask_login import login_required, current_user
from markupsafe import escape
import MySQLdb.cursors

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    with current_app.app_context():  # <-- Add this context manager
        if request.method == "POST":
            conn = current_app.config['MYSQL'].connection
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            id_user = current_user.id
            # Check Users Account Type
            cursor.execute("Select Account_Type FROM Account WHERE idAccount = %s", (id_user,))
            account_type = cursor.fetchone()['Account_Type']
            if account_type != 'Company':
                # For types that are not of Company return tools with rating of 4 stars or greater
                cursor.execute("SELECT Tools.name , Avg(Rating.rating), Tools.url, " \
                "Tools.thumbnail_url, Tools.version, Tools.pricing, Tools.description " \
                "FROM SearchIndex JOIN Rating ON SearchIndex.idIndex = Rating.idIndex " \
                "JOIN Tools ON SearchIndex.idTool = Tools.idTool GROUP BY Tools.idTool " \
                "HAVING Avg(Rating.rating) >= 4")
                results = cursor.fetchall()
            else:
                #For users who are of type Company return search history organized by date
                cursor.execute("SELECT * FROM Search_History ORDER BY created_at DESC")
                results = cursor.fetchall()


        return render_template('dashboard.html', title='Dashboard', account_type=account_type, results=results)
