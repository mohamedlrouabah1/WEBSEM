# def query_restaurants(fuseki_url, dataset_name, date_time, user_lat, user_lon, georadius, max_price, rank_by):
#     day_of_week = date_time.strftime("%A") if date_time else None
#     current_time = date_time.strftime("%H:%M") if date_time else None

#     sparql = SPARQLWrapper(f"{fuseki_url}/{dataset_name}/query")
#     # afin de renvoyé None si max_price n'est pas dans jena fuseki
#     max_price_filter = f"FILTER (xsd:decimal(?deliveryPrice) <= {max_price})" if max_price is not None else ""
#     query = f"""
#     PREFIX schema: <http://schema.org/>
#     PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

#     SELECT ?restaurant ?name ?latitude ?longitude ?deliveryPrice
#     WHERE {{
#       ?restaurant a schema:Restaurant ;
#                   schema:name ?name ;
#                   schema:address ?address .

#       ?address schema:geo ?geo .
#       ?geo schema:latitude ?latitude ;
#            schema:longitude ?longitude .

#       OPTIONAL {{
#         ?restaurant schema:potentialAction/schema:priceSpecification/schema:price ?deliveryPrice .
#         {max_price_filter}
#       }}

#       OPTIONAL {{
#         ?restaurant schema:openingHoursSpecification ?hoursSpec .
#         ?hoursSpec schema:dayOfWeek ?day ;
#                    schema:opens ?opens ;
#                    schema:closes ?closes .
#         FILTER (STR(?day) = '{day_of_week}' && ?opens <= '{current_time}' && ?closes >= '{current_time}')
#       }}
#     }}
#     """

#     sparql.setQuery(query)
#     sparql.setReturnFormat(JSON)
#     results = sparql.query().convert()

#         # Traitement des résultats
#     restaurants = {}
#     for result in results["results"]["bindings"]:
#         lat = float(result['latitude']['value']) if 'latitude' in result else None
#         lon = float(result['longitude']['value']) if 'longitude' in result else None
#         price_str = result['deliveryPrice']['value'] if 'deliveryPrice' in result else None
#         price = float(price_str.replace(',', '')) if price_str else None
#         name = result['name']['value'] if 'name' in result else "Unknown"
#         # Vérifiez si le restaurant est à la distance et au prix souhaités
#         distance = calculate_distance(user_lat, user_lon, lat, lon)
#         # Vérifier que la distance n'excède pas le geoRadius (max_distance)
#         within_distance = georadius is None or distance <= georadius
#         within_price = max_price is None or (price is not None and price <= max_price)

#         if within_distance and within_price:
#             unique_key = f"{name}-{lat}-{lon}"
#             if unique_key not in restaurants:
#                 restaurants[unique_key] = {
#                     'name': name,
#                     'price': price,
#                     'distance': distance,
#                     'latitude': lat,
#                     'longitude': lon
#                 }

#     # Tri et affichage des restaurants
#     sorted_restaurants = sorted(restaurants.values(), key=lambda x: x[rank_by])
#     for restaurant in sorted_restaurants:
#         print(f"Restaurant: {restaurant['name']}, Delivery Price: {restaurant['price']}, Distance: {restaurant['distance']:.2f} km, Latitude: {restaurant['latitude']}, Longitude: {restaurant['longitude']}")

#  query pour les rdfs sans pre formatage sur jena fuseki