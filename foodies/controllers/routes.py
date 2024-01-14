"""
Routes for the Foodies application.
"""
from argparse import Namespace
from datetime import datetime
from flask import Blueprint
from flask import jsonify, redirect, render_template, request, url_for
from models.describe import create_rdf_graph, send_data_to_fuseki
from models.query import query_restaurants, query_menu_by_name
from cache import cache
from modes import collect, describe, server
from modes import query as query_mode


main_bp = Blueprint('main', __name__)
main_bp.config = {}
main_bp.config['CACHE_TYPE'] = 'simple'

@main_bp.route('/')
def index():
    """Access to the main page of the application."""
    return render_template('index.html')


@main_bp.route('/query', methods=['POST'])
def query():
    """
    Query a sparQL endpoint of JENA to retrieve restaurants that match the user's preferences.
    """
    now = datetime.now()
    data = request.get_json()
    print(data)
    print("----------------")
    max_distance = data.get('maxDistance')
    price = data.get('deliveryPrice')
    rank_by = data.get('rankby')
    if not max_distance:
        max_distance = 100
    if not price:
        price = 114.00
    if not rank_by:
        rank_by = 'distance'

    lat = data.get('lat')
    lon = data.get('lon')
    current_time = data.get('openingHours')
    day_of_week = data.get('openingDays')
    if not current_time :
        current_time = now.strftime("%H:%M")
    if not day_of_week :
        day_of_week = now.strftime("%A")
    print(max_distance,price, rank_by, current_time, day_of_week, lat, lon)
    print("----------------")
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
    """Upload user preferences on the LDP."""

    try:
        data = request.get_json()
        print(data, file=sys.stderr)

        if LdpFuseki().upload_ldjson(data['name']):
            return jsonify({'message': 'Préférences enregistrées avec succès'})

        return jsonify({'message': 'Échec de la validation SHACL'})

    except FileNotFoundError:
        return jsonify({'message': 'Fichier SHACL introuvable'})

    except Exception as e:
        print(f"Error uploading user preferences: {e}")
        return jsonify({'message': 'Erreur lors de l\'enregistrement des préférences'}), 500



@main_bp.route('/menu', methods=['POST'])
def query_menu_by_id():
    """
    Query a SPARQL endpoint to retrieve the menu of a specific restaurant by ID.
    """
    try:
        data = request.get_json()
        restaurant_id = data.get('restaurant_id')
        print(f"Restaurant ID: {restaurant_id}")
        if not restaurant_id:
            return jsonify({'message': 'Restaurant ID is required in the request.'}), 400

        menu_data = query_menu_by_name(restaurant_id)

        # Check if menu data is available
        if menu_data and 'menu' in menu_data:
            return jsonify(menu_data)

        # Return a message if no menu data is available
        return jsonify({'message': 'Menu not found for the given restaurant ID.'}), 404

    except Exception as e:
        print(f"Error querying menu: {e}")
        return jsonify({'message': 'Error querying menu data.'}), 500




##### simulate the CLI via HTTP #####

def parse_http_arguments() -> Namespace:
    """
    Parse HTTP arguments for the main program.
    """
    args = Namespace()

    args.mode = request.args.get('mode', default='query')

    args.init_fuseki = request.args.get('init-fuseki', default=False, type=bool)
    args.upload = request.args.get('upload', default=False, type=bool)

    now = datetime.now()

    args.day_of_week = request.args.get('day-of-week', default=now.strftime("%A"))
    args.time = request.args.get('time', default=now.strftime("%H:%M"))
    args.latitude = request.args.get('latitude', default=None)
    args.longitude = request.args.get('longitude', default=None)
    args.distance = request.args.get('distance', default=1000, type=float)
    args.price = request.args.get('price', default=114.00, type=float)
    args.type_of_food = request.args.get('type-of-food', default=None)
    args.rank_by = request.args.get('rank-by', default='distance')

    args.fetch = request.args.get('fetch', default=None)

    return args


@main_bp.route('/main', methods=['GET'])
def simulate_command_line():
    """
    Endpoint to simulate the behavior of the CLI using http requests.
    """
    try:
        # Analyser les arguments HTTP
        args = parse_http_arguments()

        # Exécuter le programme principal en fonction du mode spécifié
        if args.mode == 'collect':
            collect(args.upload, args.init_fuseki)
            return jsonify({'status': 'success', 'message': 'Collect operation completed.'})

        elif args.mode == 'query':
            res = query_mode(args)
            return jsonify({'status': 'success', 'results': res})

        elif args.mode == 'describe':
            res = describe(args.fetch)
            return jsonify({'status': 'success', 'description_results': res})

        elif args.mode == 'server':
            server()

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
