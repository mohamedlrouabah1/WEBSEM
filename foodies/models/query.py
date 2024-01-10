from __future__ import annotations
import sys
import geopy.distance
from SPARQLWrapper import SPARQLWrapper, JSON
sys.path.append('../foodies')
from foodies.config import LDP_URL


def calculate_distance(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]:
        return float('inf')

    # Création des tuples de coordonnées
    coord2 = (lat1, lon1)
    coord1 = (lat2, lon2)

    # Calcul de la distance en utilisant geopy
    dist = geopy.distance.geodesic(coord1, coord2).km  # Résultat en km

    return dist


def query_restaurants(user_lat, user_lon, georadius, current_time, day_of_week, max_price, rank_by) -> list:

    # Filtre pour le prix maximum
    max_price_filter = f"FILTER (xsd:decimal(?deliveryPrice) <= {max_price})" if max_price is not None else ""
    # Filtre pour les horaires d'ouverture
    time_filter = f"FILTER (STR(?day) = '{day_of_week}' && ?opens <= '{current_time}' && ?closes >= '{current_time}')" if day_of_week and current_time else ""

    sparql = SPARQLWrapper(f'{LDP_URL}/query')

    query = f"""
     PREFIX schema: <http://schema.org/>
     PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

     SELECT ?graph ?restaurant ?name ?latitude ?longitude ?description ?image ?url ?streetAddress ?telephone ?day ?opens ?closes
     WHERE {{
       GRAPH ?graph {{
           ?restaurant a schema:Restaurant ;
                       schema:name ?name ;
                       schema:address ?addressURL .
           OPTIONAL {{ ?restaurant schema:description ?description . }}
           OPTIONAL {{ ?restaurant schema:image ?image . }}
           OPTIONAL {{ ?restaurant schema:sameAs ?url . }}

           ?addressURL a schema:PostalAddress ;
                       schema:streetAddress ?streetAddress ;
                       schema:telephone ?telephone ;
                       schema:geo ?geo .
           ?geo schema:latitude ?latitude ;
                schema:longitude ?longitude .

           OPTIONAL {{
             ?restaurant schema:openingHoursSpecification ?openingHoursSpec .
             ?openingHoursSpec schema:opens ?opens ;
                               schema:closes ?closes ;
                               schema:dayOfWeek ?day .
           }}
           OPTIONAL {{
               ?restaurant schema:potentialAction/schema:priceSpecification/schema:price ?deliveryPrice .
                {max_price_filter}
            }}
           OPTIONAL {{
                {time_filter}
            }}
       }}
     }}
     """
    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        georadius = float(georadius) if georadius is not None else None # Convert to float if not None
        restaurant_dict = {}
        for result in results["results"]["bindings"]:
            graph = result['graph']['value']
            lat = float(result['latitude']['value']) if 'latitude' in result else None
            lon = float(result['longitude']['value']) if 'longitude' in result else None
            name = result['name']['value'] if 'name' in result else "Unknown"
            price_str = result.get('deliveryPrice', {}).get('value')
            price = float(price_str.replace(',', '')) if price_str else None
            description = result.get('description', {}).get('value', '')
            image = result.get('image', {}).get('value', '')
            url = result.get('url', {}).get('value', '')
            address = result.get('streetAddress', {}).get('value', '')
            telephone = result.get('telephone', {}).get('value', '')

            distance = calculate_distance(user_lat, user_lon, lat, lon) if lat and lon else None
            if distance is None or (georadius is not None and distance > georadius):
                continue

            key = (graph, name, lat, lon, description, image, url, address, telephone)
            if key not in restaurant_dict:
                restaurant_dict[key] = {
                    'graph': graph,
                    'name': name,
                    'latitude': lat,
                    'longitude': lon,
                    'description': description,
                    'image': image,
                    'url': url,
                    'address': address,
                    'telephone': telephone,
                    'openingHours': [],
                    'distance': distance,
                    'price': price
                }

            opening_hours_str = f"{result.get('opens', {}).get('value', '')} - {result.get('closes', {}).get('value', '')}, Days: {result.get('day', {}).get('value', '')}"
            if opening_hours_str not in restaurant_dict[key]['openingHours']:
                restaurant_dict[key]['openingHours'].append(opening_hours_str)

        restaurants = list(restaurant_dict.values())

        # Trier les restaurants en fonction de 'rank_by'
        if rank_by == 'distance':
            restaurants = sorted(restaurants, key=lambda x: x['distance'] if x['distance'] is not None else float('inf'))
        elif rank_by == 'price':
            restaurants = sorted(restaurants, key=lambda x: x['price'] if x['price'] is not None else float('inf'))

        print(restaurants)
        return restaurants

    except Exception as e:
        print(f"Error querying Fuseki: {e}")
        return []


def query_menu_by_name(graph_name):
    sparql = SPARQLWrapper(f'{LDP_URL}/query')
    query = f"""
     PREFIX ns1: <http://schema.org/>
     PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

     SELECT ?menuItemName ?menuItemDescription ?menuItemPrice ?menuItemImage
     WHERE {{
       GRAPH <{graph_name}> {{
         ?menuItem a ns1:MenuItem ;
           ns1:name ?menuItemName .
         OPTIONAL {{ ?menuItem ns1:description ?menuItemDescription . }}
         OPTIONAL {{ ?menuItem ns1:price ?menuItemPrice . }}
         OPTIONAL {{ ?menuItem ns1:image ?menuItemImage . }}
       }}
     }}
     """

    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        menu_data = []
        for result in results["results"]["bindings"]:
            name = result['menuItemName']['value'] if 'menuItemName' in result else "Unknown"
            description = result.get('menuItemDescription', {}).get('value', 'Description not available')
            price = result.get('menuItemPrice', {}).get('value', 'Price not available')
            image = result.get('menuItemImage', {}).get('value', 'Image URL not available')

            menu_item = {
                'name': name,
                'description': description,
                'price': price,
                'image': image
            }
            menu_data.append(menu_item)

        return {'menu': menu_data}
    except Exception as e:
        print(f"Erreur lors de la requête du menu : {e}")
        return {}