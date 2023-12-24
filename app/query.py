from SPARQLWrapper import SPARQLWrapper, JSON
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]:
        return float('inf')

    R = 6371  # Rayon de la Terre en km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance



def query_restaurants(fuseki_url, dataset_name, date_time, user_lat, user_lon, georadius, max_price, rank_by):
    day_of_week = date_time.strftime("%A") if date_time else ""
    current_time = date_time.strftime("%H:%M") if date_time else ""
    max_price_filter = f"FILTER (xsd:decimal(?deliveryPrice) <= {max_price})" if max_price is not None else ""

    sparql = SPARQLWrapper(f"{fuseki_url}/{dataset_name}/query")
    query = f"""
    PREFIX schema: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?graph ?restaurant ?name ?latitude ?longitude ?deliveryPrice
    WHERE {{
      GRAPH ?graph {{
        ?restaurant a schema:Restaurant ;
                    schema:name ?name ;
                    schema:address ?address .

        ?address schema:geo ?geo .
        ?geo schema:latitude ?latitude ;
             schema:longitude ?longitude .

        OPTIONAL {{
          ?restaurant schema:potentialAction/schema:priceSpecification/schema:price ?deliveryPrice .
          {max_price_filter}
        }}

        OPTIONAL {{
          ?restaurant schema:openingHoursSpecification ?hoursSpec .
          ?hoursSpec schema:dayOfWeek ?day ;
                     schema:opens ?opens ;
                     schema:closes ?closes .
          FILTER (STR(?day) = '{day_of_week}' && ?opens <= '{current_time}' && ?closes >= '{current_time}')
        }}
      }}
    }}
    ORDER BY ?graph
    """

    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        restaurants = {}
        for result in results["results"]["bindings"]:
            graph = result['graph']['value']
            lat = float(result['latitude']['value']) if 'latitude' in result else None
            lon = float(result['longitude']['value']) if 'longitude' in result else None
            price_str = result.get('deliveryPrice', {}).get('value')
            price = float(price_str.replace(',', '')) if price_str else None
            name = result['name']['value'] if 'name' in result else "Unknown"

            distance = calculate_distance(user_lat, user_lon, lat, lon) if lat and lon else None
            if distance is None or (georadius is not None and distance > georadius):
                continue
            unique_key = f"{graph}-{name}-{lat}-{lon}"
            if unique_key not in restaurants:
                restaurants[unique_key] = {
                    'graph': graph,
                    'name': name,
                    'price': price,
                    'distance': distance,
                    'latitude': lat,
                    'longitude': lon
                }

        sorted_restaurants = sorted(restaurants.values(), key=lambda x: x[rank_by])
        for restaurant in sorted_restaurants:
            print(f"Graph: {restaurant['graph']}, Restaurant: {restaurant['name']}, Delivery Price: {restaurant['price']}, Distance: {restaurant['distance']:.2f} km, Latitude: {restaurant['latitude']}, Longitude: {restaurant['longitude']}")

    except Exception as e:
        print(f"Error querying Fuseki: {e}")