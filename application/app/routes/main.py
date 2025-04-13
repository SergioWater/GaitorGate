from flask import Blueprint, render_template, request, redirect, session
from flask_login import login_required, current_user
from markupsafe import escape

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

@main_bp.route('/account')
@login_required
def account():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT username, email FROM Account WHERE idAccount = %s", (current_user.id,))
    account_info = cursor.fetchone()
    cursor.close()
    title = f"{account_info['username']}'s Account"
    return render_template('account.html', user=account_info, active_page='account', title=title)
