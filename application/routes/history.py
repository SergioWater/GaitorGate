from flask import Blueprint, current_app
from flask_login import current_user

history_bp = Blueprint("history", __name__)


@history_bp.route("/history", methods=["GET"])
# @login_required
def history():
    conn = current_app.config["MYSQL"].connection
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM Search_History
        WHERE idAccount = %s
    """,
        (current_user.get_id(),),
    )

    return f"{cursor.fetchall()}"
