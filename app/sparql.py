from SPARQLWrapper import SPARQLWrapper, JSON
import datetime
import math

def query_restaurants_open_at(fuseki_url, dataset_name, now):
    # Get current date and time
    # now = datetime.datetime.now()
    day_of_week = now.strftime("%A")
    current_time = now.strftime("%H:%M")

    sparql = SPARQLWrapper(f"{fuseki_url}/{dataset_name}/query")
    query = f"""
    PREFIX schema: <http://schema.org/>

    SELECT ?restaurant ?name ?opens ?closes
    WHERE {{
      ?restaurant a schema:Restaurant ;
                  schema:name ?name ;
                  schema:openingHoursSpecification ?hoursSpec .

      ?hoursSpec schema:opens ?opens ;
                 schema:closes ?closes ;
                 schema:dayOfWeek ?day .

      FILTER (STR(?day) = "{day_of_week}" && ?opens <= "{current_time}" && ?closes >= "{current_time}")
    }}
    LIMIT 10
    """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        print(f"Restaurant: {result['restaurant']['value']}, Name: {result['name']['value']}, Opens: {result['opens']['value']}, Closes: {result['closes']['value']}")



def calculate_distance(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]:
        return float('inf')  # Return a large value to signify 'no distance'

    R = 6371  # Earth radius in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance


def query_restaurants(fuseki_url, dataset_name, date_time, user_lat, user_lon, max_distance, max_price, rank_by):
    day_of_week = date_time.strftime("%A") if date_time else None
    current_time = date_time.strftime("%H:%M") if date_time else None

    sparql = SPARQLWrapper(f"{fuseki_url}/{dataset_name}/query")
    query = f"""
    PREFIX schema: <http://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?restaurant ?name ?latitude ?longitude ?deliveryPrice
    WHERE {{
      ?restaurant a schema:Restaurant ;
                  schema:name ?name ;
                  schema:address ?address .

      ?address schema:geo ?geo .
      ?geo schema:latitude ?latitude ;
           schema:longitude ?longitude .

      OPTIONAL {{
        ?restaurant schema:potentialAction/schema:priceSpecification/schema:price ?deliveryPrice .
      }}

      OPTIONAL {{
        ?restaurant schema:openingHoursSpecification ?hoursSpec .
        ?hoursSpec schema:dayOfWeek ?day ;
                   schema:opens ?opens ;
                   schema:closes ?closes .
        FILTER (STR(?day) = '{day_of_week}' && ?opens <= '{current_time}' && ?closes >= '{current_time}')
      }}
    }}
    """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    restaurants = {}
    for result in results["results"]["bindings"]:
        lat = float(result['latitude']['value']) if 'latitude' in result else None
        lon = float(result['longitude']['value']) if 'longitude' in result else None
        price_str = result['deliveryPrice']['value'] if 'deliveryPrice' in result else None
        price = float(price_str.replace(',', '')) if price_str else None
        name = result['name']['value'] if 'name' in result else "Unknown"

        distance = calculate_distance(user_lat, user_lon, lat, lon)

        if max_distance is None or distance <= max_distance:
            unique_key = f"{name}-{lat}-{lon}" if lat is not None and lon is not None else name

            if unique_key not in restaurants:
                restaurants[unique_key] = {
                    'name': name,
                    'price': price,
                    'distance': distance,
                    'latitude': lat,
                    'longitude': lon
                }
    
    sorted_restaurants = sorted(restaurants.values(), key=lambda x: x[rank_by] if x[rank_by] is not None else float('inf'))

    for restaurant in sorted_restaurants:
        print(f"Restaurant: {restaurant['name']}, Delivery Price: {restaurant['price']}, Distance: {restaurant['distance']:.2f} km, Latitude: {restaurant['latitude']}, Longitude: {restaurant['longitude']}")
