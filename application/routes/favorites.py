from flask import Blueprint, render_template, request, redirect, session, current_app, url_for
from flask_login import login_required, current_user
import MySQLdb.cursors

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    """Add or remove a favorite"""
    with current_app.app_context():
        conn = current_app.config['MYSQL'].connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        index_id = request.form.get('index_id')
        
        # First get the idUser from the Account table
        cursor.execute(
            "SELECT idUser FROM Account WHERE idAccount = %s",
            (current_user.id,)
        )
        user_result = cursor.fetchone()
        
        if not user_result:
            print(f"Could not find User ID for Account ID {current_user.id}")
            return redirect(request.referrer or url_for('search.search'))
            
        user_id = user_result['idUser']
        
        # Check if this is already a favorite
        cursor.execute(
            "SELECT idFavorite FROM Favorite WHERE idUser = %s AND idIndex = %s",
            (user_id, index_id)
        )
        existing_favorite = cursor.fetchone()
        
        if existing_favorite:
            # Remove favorite
            cursor.execute(
                "DELETE FROM Favorite WHERE idUser = %s AND idIndex = %s",
                (user_id, index_id)
            )
            print(f"Removed favorite for User ID {user_id}, Index ID {index_id}")
        else:
            # Add favorite
            cursor.execute(
                "INSERT INTO Favorite (idUser, idIndex) VALUES (%s, %s)",
                (user_id, index_id)
            )
            print(f"Added favorite for User ID {user_id}, Index ID {index_id}")
        
        conn.commit()
        cursor.close()
        
        # Redirect back to the previous page
        referrer = request.referrer or url_for('search.search')
        return redirect(referrer)


@favorites_bp.route('/saved', methods=['GET'])
@login_required
def view_saved():
    """View all saved favorites for the current user"""
    with current_app.app_context():
        conn = current_app.config['MYSQL'].connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # First get the idUser from the Account table
        cursor.execute(
            "SELECT idUser, username, email FROM Account WHERE idAccount = %s",
            (current_user.id,)
        )
        user_result = cursor.fetchone()
        
        if not user_result:
            print(f"Could not find User ID for Account ID {current_user.id}")
            return render_template('saved.html', data=[], user={'username': 'User'}, title="Favorites")
            
        user_id = user_result['idUser']
        username = user_result['username']
        email = user_result.get('email', '')
        
        # Get all favorites with tool information
        cursor.execute("""
            SELECT 
                f.idFavorite, 
                si.idIndex,
                t.idTool,
                t.description,
                t.name,
                t.company,
                t.url,
                t.thumbnail_url,
                t.published_date,
                t.pricing,
                t.version,
                c.name AS category,
                p.name AS platform
            FROM Favorite f
            JOIN SearchIndex si ON f.idIndex = si.idIndex
            JOIN Tools t ON si.idTool = t.idTool
            LEFT JOIN Category c ON si.idCategory = c.idCategory
            LEFT JOIN Platform p ON si.idPlatform = p.idPlatform
            WHERE f.idUser = %s
            ORDER BY f.idFavorite DESC
        """, (user_id,))
        
        favorites = cursor.fetchall()
        cursor.close()
        
        title = f"{username}'s Favorites"
        return render_template(
            'saved.html',
            data=favorites,
            user={'username': username, 'email': email},
            title=title
        )

# Helper function to check if an item is favorited
def is_favorited(index_id, user_id):
    """Check if an item is favorited by the user"""
    if not user_id:
        return False
        
    with current_app.app_context():
        conn = current_app.config['MYSQL'].connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # First get the idUser from the Account table
        cursor.execute(
            "SELECT idUser FROM Account WHERE idAccount = %s",
            (user_id,)
        )
        user_result = cursor.fetchone()
        
        if not user_result:
            return False
            
        actual_user_id = user_result['idUser']
        
        cursor.execute(
            "SELECT 1 FROM Favorite WHERE idUser = %s AND idIndex = %s",
            (actual_user_id, index_id)
        )
        result = cursor.fetchone() is not None
        cursor.close()
        return result 