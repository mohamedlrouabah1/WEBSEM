import json
import os

from datetime import datetime
from flask import Blueprint
from flask import jsonify, redirect, render_template, request, session, url_for
from models.collect import shacl_validation, collect, send_collect_to_fuseki
from models.describe import *
from models.query import query_restaurants
from flask_caching import Cache

main_bp = Blueprint('main', __name__)
main_bp.config = {}
main_bp.config['CACHE_TYPE'] = 'simple'
cache_main = Cache(config={'CACHE_TYPE': 'simple'})


@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dev')
def dev_page():
    return render_template('dev.html')


@main_bp.route('/collect-data', methods=['POST'])
def collect_data_route():
    url = request.json.get('url')
    collect(url)
    result = jsonify({'message': 'Données collectées avec succès'})
    return render_template('dev.html' , result=result)

@main_bp.route('/send-to-fuseki', methods=['POST'])
def send_to_fuseki():
    fuseki_url = "http://localhost:3030"
    dataset_name = "foodies"
    try:
        with open("collect.json", "r") as file:
            data = json.load(file)
    except Exception as e:
        return render_template('dev.html' , result=jsonify({'message': f'Erreur lors de la lecture du fichier collect.json : {e}'}))

    send_collect_to_fuseki(fuseki_url, dataset_name, data)
    return render_template('dev.html' , result=jsonify({'message': 'Données envoyées avec succès'}))


@main_bp.route('/query', methods=['POST'])
def query():
    """
    Query a sparQL endpoint of JENA to retrieve restaurants that match the user's preferences.
    """
    fuseki_url = "http://localhost:3030"
    dataset_name = "foodies"
    now = datetime.now()
    data = request.get_json()
    print(data)

    max_distance = data.get('maxDistance', 30)  # default value if not provided
    price = data.get('deliveryPrice', 114.00)  # default value if not provided
    rank_by = data.get('rankby')
    print(rank_by)
    if rank_by is None:
        rank_by = 'distance'  # Default ranking
    lat = data.get('lat')  # lat might be None
    lon = data.get('lon')  # lon might be None
    current_time = data.get('openingHours')
    day_of_week = data.get('openingDays')
    print(current_time)
    print(day_of_week)
    if not day_of_week:  # If openingDays is not provided, use the current day
        day_of_week = now.strftime("%A")

    if not current_time:  # If openingHours is not provided, use the current time
        current_time = now.strftime("%H:%M")

    # Check if lat and lon are provided
    if lat is not None and lon is not None:
        results = query_restaurants(
            fuseki_url, dataset_name,
            lat, lon, max_distance,
            current_time, day_of_week,
            price, rank_by)
    else:
        # Handle cases when lat and lon are not provided
        # Maybe return a default list of restaurants or a specific message
        results = []

    cache_key = f"restaurants_{datetime.now().timestamp()}"
    cache_main.set(cache_key, results, timeout=200)
    return redirect(url_for('show_restaurants', key=cache_key))

@main_bp.route('/restaurants', methods=['GET'])
def show_restaurants():
    cache_key = request.args.get('key')
    restaurants_data = cache_main.get(cache_key) if cache_key else []

    return render_template('restaurants.html', restaurants=restaurants_data)

@main_bp.route('/preferences', methods=['POST'])
def preferences():
    fuseki_url = "http://localhost:3030"
    dataset_name = "preferences"
    try:
        data = request.get_json()
        print(data)
        rdf_graph = create_rdf_graph(data)

        if shacl_validation(data):
            send_data_to_fuseki(fuseki_url, dataset_name, rdf_graph, data['name'])
            return jsonify({'message': 'Préférences enregistrées avec succès'})
        else:
            return jsonify({'message': 'Échec de la validation SHACL'})

    except FileNotFoundError:
        return jsonify({'message': 'Fichier SHACL introuvable'})
    except Exception as e:
        return jsonify({'message': f'Erreur lors de la validation : {e}'})

@main_bp.route('/user-preferences', methods=['POST'])
def user_preferences():
    # Retrieve data from POST request
    data = json.loads(request.data)
    username = data.get('username')

    fuseki_url = os.getenv("FUSEKI_URL","http://localhost:3030")
    dataset_name = os.getenv("FUSEKI_DATASET_NAME", "foodies")

    # Fetch user preferences based on username
    user_prefs = fetch_user_preferences(username)
    if not isinstance(user_prefs, dict):
        # Handle error or invalid return type
        print(f"Invalid user preferences returned for username {username}")
        return jsonify({'success': False, 'message': 'Invalid user preferences'})

    # Assign default values if necessary
    if user_prefs.get('max_distance') is None:
        user_prefs['max_distance'] = 10  # Default value
    if user_prefs.get('price') is None:
        user_prefs['price'] = 114.00  # Default value

    # Other variables (like 'rank_by') might need similar handling
    rank_by = user_prefs.get('rank_by', 'distance')  # Default to 'distance' if not provided

    now = datetime.now()
    day_of_week = now.strftime("%A")
    current_time = now.strftime("%H:%M")
    results = query_restaurants(fuseki_url, dataset_name, user_prefs.get('lat'), user_prefs.get('lon'), user_prefs['max_distance'],current_time, day_of_week, user_prefs['price'], rank_by)
    cache_key = f"restaurants_{datetime.now().timestamp()}"
    cache_main.set(cache_key, results, timeout=200)
    return redirect(url_for('show_restaurants', key=cache_key))
