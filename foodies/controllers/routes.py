"""
Routes for the Foodies application.
"""
import sys
import subprocess
from argparse import Namespace
from datetime import datetime
from flask import Blueprint
from flask import jsonify, redirect, render_template, request, url_for
from models.describe import describe_user_preferences
from models.query import query_restaurants
from cache import cache
from coopcycle_scrapper.ldp_fuseki import LdpFuseki
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
    """Upload user preferences on the LDP."""
    try:
        data = request.get_json()
        print(data, file=sys.stderr)

        if LdpFuseki().upload_ldjson(data['name']):
            return jsonify({'message': 'Préférences enregistrées avec succès'})
        else:
            return jsonify({'message': 'Échec de la validation SHACL'})

    except FileNotFoundError:
        return jsonify({'message': 'Fichier SHACL introuvable'})
    except Exception as e:
        return jsonify({'message': f'Erreur lors de la validation : {e}'})


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
        args = parse_http_arguments()

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