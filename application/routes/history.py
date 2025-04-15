from flask import Blueprint, current_app
from flask_login import current_user

history_bp = Blueprint("history", __name__)


@history_bp.route("/history", methods=["GET"])
@login_required
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

    data = cursor.fetchall()

    cursor.execute("SELECT username, email FROM Account WHERE idAccount = %s", (current_user.id,))

    account_info = cursor.fetchone()

    cursor.close()
    title = f"{account_info['username']}'s History"
    return render_template('history.html', user=account_info, data=data, title=title)