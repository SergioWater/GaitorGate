from flask import Blueprint, render_template, request, redirect, session, current_app,url_for
from flask_login import login_required, current_user
from markupsafe import escape
import MySQLdb.cursors
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template("index.html", data=[], current_page=1, total_pages=0, title='Gaitor Gate')

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
    cursor.execute("SELECT username, email FROM Account WHERE idAccount = %s", (current_user.id,))
    account_info = cursor.fetchone()
    cursor.close()
    title = f"{account_info['username']}'s Account"
    return render_template('account.html', user=account_info, active_page='account', title=title)

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html', title=title)


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
