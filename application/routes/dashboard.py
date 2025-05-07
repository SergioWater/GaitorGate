from flask import Blueprint, render_template, request, redirect, session, current_app,url_for
from flask_login import login_required, current_user
from markupsafe import escape
import MySQLdb.cursors

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    print("IN DASHBOARD ROUTE")
    with current_app.app_context():  # <-- Add this context manager
        conn = current_app.config['MYSQL'].connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        id_user = current_user.id
        # Check Users Account Type
        cursor.execute("Select Account_Type FROM Account WHERE idAccount = %s", (id_user,))
        account_type = cursor.fetchone()['Account_Type']
        if account_type == 'Company':
            print("IN DASHBOARD ROUTE IF BLOCK COMPANY")

            # Display summary of Company's tool
            cursor.execute("SELECT Company.company_name, Tools.name, " \
            "Company.website, Tools.url, Tools.thumbnail_url, Tools.version, " \
            "Tools.pricing, Tools.description " \
            "FROM Account " \
            "JOIN Company ON Account.idAccount = Company.idAccount " \
            "JOIN Tools ON Company.idAccount = Tools.company " \
            "WHERE Account.idAccount = %s", (id_user,))
            tool_summary_results = cursor.fetchall()

            # Get reviews that were posted for this company 
            cursor.execute("SELECT Tools.name, Review.review_text, Review_created_at " \
            "FROM Account " \
            "JOIN Company ON Account.idAccount = Company.idAccount " \
            "JOIN Tools ON Company.idAccount = Tools.company " \
            "JOIN SearchIndex ON Tools.idTool = SearchIndex.idTool " \
            "JOIN Review ON SearchIndex.idIndex = Review.idIndex " \
            "WHERE Account.idAccount = %s " \
            "ORDER BY Review.created_at DESC", (id_user,))
            review_results = cursor.fetchall()
            

        else:
            print("IN DASHBOARD ROUTE IF NOT COMPANY BLOCK STATEMENT")

            #Display reviews that users posted
            cursor.execute("SELECT Review.idAccount, Review.review_text, Review.created_at, Tools.name " \
            "FROM Account " \
            "JOIN Review ON Account.idAccount = Review.idAccount " \
            "JOIN SearchIndex ON Review.idIndex = SearchIndex.idIndex " \
            "JOIN Tools ON SearchIndex.idTool = Tools.idTool " \
            "WHERE Account.idAccount = %s ", (id_user,))
            review_results = cursor.fetchall()
            print(review_results)
            print(id_user)
            
        cursor.close()

        return render_template(
            'index.html',
            title='Dashboard',
            account_type=account_type,
            tool_summary=tool_summary_results if account_type == 'Company' else None,
            reviews=review_results
        )