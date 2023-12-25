from datetime import datetime
from app import app
from flask import redirect, render_template, request, session, url_for
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
    rank_by = 'distance'  # Default ranking
    data = request.get_json()
    print(data)
    max_distance = 10  # Maximum distance in kilometers
    price = 114.00 
    results = query_restaurants(fuseki_url, dataset_name, now, data['lat'], data['lon'], max_distance, price, rank_by)
    session['restaurants'] = results  # Stocker les résultats dans la session
    return redirect(url_for('show_restaurants'))

@app.route('/restaurants')
def show_restaurants():
    restaurants_data = session.get('restaurants', [])
    return render_template('restaurants.html', restaurants=restaurants_data)