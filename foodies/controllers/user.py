
"""
url /user/*.
"""
import json
from datetime import datetime
from flask import Blueprint, jsonify, redirect, request, url_for

from cache import cache
from models.describe import fetch_user_preferences
from models.query import query_restaurants

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/preferences', methods=['POST'])
def user_preferences():
    """ Update user preferences in the Jena LDP. """
    # Retrieve data from POST request
    data = json.loads(request.data)
    print(data)
    username = data.get('username')
    # Fetch user preferences based on username
    user_prefs = fetch_user_preferences(username)
    if not isinstance(user_prefs, dict):
        print(f"Invalid user preferences returned for username {username}")
        return jsonify({'success': False, 'message': 'Invalid user preferences'})

    # Assign default values if necessary
    if not user_prefs.get('max_distance'):
        user_prefs['max_distance'] = 10
    if not user_prefs.get('price') :
        user_prefs['price'] = 114.00

    # Other variables (like 'rank_by') might need similar handling
    rank_by = user_prefs.get('rank_by', 'distance')  # Default to 'distance' if not provided

    now = datetime.now()
    day_of_week = now.strftime("%A")
    current_time = now.strftime("%H:%M")
    results = query_restaurants(
        user_prefs.get('lat'), user_prefs.get('lon'),  user_prefs['max_distance'],
        current_time, day_of_week, user_prefs['price'], rank_by
        )
    cache_key = f"restaurants_{datetime.now().timestamp()}"
    cache.set(cache_key, results, timeout=200)
    return redirect(url_for('main.show_restaurants', key=cache_key, _external=True))
