"""
Routes for the Foodies application.
"""
import json
import os
import sys

from datetime import datetime
from flask import Blueprint
from flask import jsonify, redirect, render_template, request, url_for
from models.collect import shacl_validation, collect, send_collect_to_fuseki
from models.describe import create_rdf_graph, fetch_user_preferences, send_data_to_fuseki
from models.query import query_restaurants
from cache import cache


main_bp = Blueprint('main', __name__)
main_bp.config = {}
main_bp.config['CACHE_TYPE'] = 'simple'

@main_bp.route('/')
def index():
    """Access to the main page of the application."""
    return render_template('index.html')

@main_bp.route('/dev')
def dev_page():
    """Access to the Debbug page of the application."""
    return render_template('dev.html')


@main_bp.route('/collect-data', methods=['POST'])
def collect_data_route():
    """Collect user preferences get from the index page."""
    url = request.json.get('url')
    collect(url)
    result = jsonify({'message': 'Données collectées avec succès'})
    return render_template('dev.html' , result=result)

@main_bp.route('/send-to-fuseki', methods=['POST'])
def send_to_fuseki():
    """Upload json files to the linked data platform."""
    try:
        with open("collect.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        send_collect_to_fuseki(data)
        return render_template('dev.html' , result=jsonify({'message': 'Données envoyées avec succès'}))

    except Exception as e:
        return render_template(
            'dev.html' ,
            result=jsonify({'message': f'Erreur lors de la lecture du fichier collect.json : {e}'})
            )


@main_bp.route('/query', methods=['POST'])
def query():
    """
    Query a sparQL endpoint of JENA to retrieve restaurants that match the user's preferences.
    """
    now = datetime.now()
    data = request.get_json()
    print(data)

    max_distance = data.get('maxDistance', 30)
    price = data.get('deliveryPrice', 114.00)
    rank_by = data.get('rankby', 'distance')
    lat = data.get('lat', None)
    lon = data.get('lon', None)
    current_time = data.get('openingHours', now.strftime("%H:%M"))
    day_of_week = data.get('openingDays', now.strftime("%A"))

    print(rank_by, current_time, day_of_week, sep="\n", file=sys.stderr)

    # Check if lat and lon are provided
    if lat is not None and lon is not None:
        results = query_restaurants(
            lat, lon, max_distance,
            current_time, day_of_week,
            price, rank_by)
    else:
        # Handle cases when lat and lon are not provided
        # Maybe return a default list of restaurants or a specific message
        results = []

    cache_key = f"restaurants_{datetime.now().timestamp()}"
    cache.set(cache_key, results, timeout=200)
    return redirect(url_for('main.show_restaurants', key=cache_key))

@main_bp.route('/restaurants', methods=['GET'])
def show_restaurants():
    """Get restaurant details"""
    cache_key = request.args.get('key')
    restaurants_data = cache.get(cache_key) if cache_key else []

    return render_template('restaurants.html', restaurants=restaurants_data)

@main_bp.route('/preferences', methods=['POST'])
def preferences():
    try:
        data = request.get_json()
        print(data)
        rdf_graph = create_rdf_graph(data)

        if shacl_validation(data):
            send_data_to_fuseki(rdf_graph, data['name'])
            return jsonify({'message': 'Préférences enregistrées avec succès'})
        else:
            return jsonify({'message': 'Échec de la validation SHACL'})

    except FileNotFoundError:
        return jsonify({'message': 'Fichier SHACL introuvable'})
    except Exception as e:
        return jsonify({'message': f'Erreur lors de la validation : {e}'})

@main_bp.route('/user-preferences', methods=['POST'])
def user_preferences():
    """ Update user preferences in the Jena LDP. """
    # Retrieve data from POST request
    data = json.loads(request.data)
    username = data.get('username')

    # Fetch user preferences based on username
    user_prefs = fetch_user_preferences(username)
    if not isinstance(user_prefs, dict):
        # Handle error or invalid return type
        print(f"Invalid user preferences returned for username {username}")
        return jsonify({'success': False, 'message': 'Invalid user preferences'})

    # Assign default values if necessary
    if user_prefs.get('max_distance') is None:
        user_prefs['max_distance'] = 10
    if user_prefs.get('price') is None:
        user_prefs['price'] = 114.00

    # Other variables (like 'rank_by') might need similar handling
    rank_by = user_prefs.get('rank_by', 'distance')  # Default to 'distance' if not provided

    now = datetime.now()
    day_of_week = now.strftime("%A")
    current_time = now.strftime("%H:%M")
    results = query_restaurants(user_prefs.get('lat'), user_prefs.get('lon'), user_prefs['max_distance'],current_time, day_of_week, user_prefs['price'], rank_by)
    cache_key = f"restaurants_{datetime.now().timestamp()}"
    cache.set(cache_key, results, timeout=200)
    return redirect(url_for('show_restaurants', key=cache_key))
