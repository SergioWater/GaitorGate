from flask import Blueprint, render_template, request, redirect, session, current_app,url_for
from flask_login import login_required, current_user
from markupsafe import escape
import MySQLdb.cursors
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        with current_app.app_context():
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
                cursor.execute("SELECT Tools.name, Review.review_text, Review.created_at " \
                               "FROM Account " \
                               "JOIN Company ON Account.idAccount = Company.idAccount " \
                               "JOIN Tools ON Company.idAccount = Tools.company " \
                               "JOIN SearchIndex ON Tools.idTool = SearchIndex.idTool " \
                               "JOIN Review ON SearchIndex.idIndex = Review.idIndex " \
                               "WHERE Account.idAccount = %s " \
                               "ORDER BY Review.created_at DESC", (id_user,))
                review_results = cursor.fetchall()
                cursor.close()
                return render_template(
                    'index.html',
                    title='Dashboard',
                    account_type=account_type,
                    tool_summary=tool_summary_results,
                    reviews=review_results
                )
            elif account_type in ('General', 'Student'):
                print("IN DASHBOARD ROUTE IF NOT COMPANY BLOCK STATEMENT")
                # Display reviews that users posted
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
            else:
                return render_template(
                    'index.html',
                    title='Gaitor Gate'
                )
    else:
        return render_template(
            'index.html',
            title='Gaitor Gate'
        )
        
@main_bp.route('/about')
def about():
    return render_template("about.html", title='About')

@main_bp.route('/members/<name>')
def team_member(name):
    return render_template(f"members/{escape(name)}.html", title=name)

@main_bp.route('/mainSearch')
def mainSearch():
    return render_template("mainSearch.html", title='Search')

@main_bp.route('/account')
@login_required
def account():
    conn = current_app.config['MYSQL'].connection
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT username, email, Account_Type FROM Account WHERE idAccount = %s", (current_user.id,))
    account_info = cursor.fetchone()
    cursor.close()
    title = f"{account_info['username']}'s Account"
    return render_template('account.html', user=account_info, active_page='account', title=title)

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html', title="title")


 # When possible this should be moved into its own file to keep up with our
@main_bp.route('/update_description', methods=['POST'])
def update_description():
    try:
        description = request.form.get('description', '')
        
        if not description:
            return redirect(url_for('main.about'))
            
        image_url = request.form.get('image_url', '')
        
        # Connect to database
        conn = current_app.config['MYSQL'].connection
        cursor = conn.cursor()
        
        # Insert into description table
        cursor.execute(
            "INSERT INTO Website_Description (description, image_url) VALUES (%s, %s)",
            (description, image_url)
        )
        
        conn.commit()
        cursor.close()
        
        return redirect(url_for('main.about'))
    except Exception as e:
        print(f"Error updating description: {e}")
        return redirect(url_for('main.about'))
