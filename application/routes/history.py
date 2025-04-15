from flask import Blueprint, current_app
from flask_login import login_user, login_required, logout_user, UserMixin, current_user
import MySQLdb.cursors

history_bp = Blueprint("history", __name__)


@history_bp.route("/history", methods=["GET"])
# @login_required
def history():
    conn = current_app.config["MYSQL"].connection
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM Search_History;
    """)

    print("USER:", current_user)

    print(cursor.fetchall())

    return [1, 2, 3]
