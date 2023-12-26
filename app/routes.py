from datetime import datetime
import json
from app import app
from flask import jsonify, redirect, render_template, request, session, url_for
from app.collect import shacl_validation
from app.describe import *
from app.query import query_restaurants


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    session.pop('restaurants', None)  # Supprime les données des restaurants si elles existent
    fuseki_url = "http://localhost:3030"
    dataset_name = "shacl"
    now = datetime.now()
   
    data = request.get_json()
    print(data)

    # if max_distance is None :
    max_distance = 10  # defaut value
    # if price is None :
    price = 114.00 # defaut value
    # if rank_by is None :
    rank_by = 'distance'  # Default ranking
    results = query_restaurants(fuseki_url, dataset_name, now, data['lat'], data['lon'], max_distance, price, rank_by)
    session['restaurants'] = results  # Stocker les résultats dans la session
    return redirect(url_for('show_restaurants'))

@app.route('/restaurants', methods=['GET'])
def show_restaurants():
    restaurants_data = session.get('restaurants', [])
    return render_template('restaurants.html', restaurants=restaurants_data)

@app.route('/preferences', methods=['POST'])
def preferences():
    fuseki_url = "http://localhost:3030"
    dataset_name = "preferencies"
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

@app.route('/user-preferences', methods=['POST'])
def user_preferences():
    session.pop('restaurants', None)  # Clear existing restaurant data

    # Retrieve data from POST request
    data = json.loads(request.data)
    username = data.get('username')

    fuseki_url = "http://localhost:3030"
    dataset_name = "shacl"

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
    results = query_restaurants(fuseki_url, dataset_name, now, user_prefs.get('lat'), user_prefs.get('lon'), user_prefs['max_distance'], user_prefs['price'], rank_by)
    session['restaurants'] = results  # Store results in session
    return redirect(url_for('show_restaurants'))
