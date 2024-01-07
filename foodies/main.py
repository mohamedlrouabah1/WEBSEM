import datetime
import sys

from models.query import  query_restaurants
from models.describe import fetch_user_preferences

def main():
    # url = "https://coopcycle.org/fr/"
    fuseki_url = "http://localhost:3030"
    dataset_name = "shacl"
    # data = collect(url)
    # load json file
    # data = json.load(open('collect.json'))
    # # validate json file
    # if shacl_validation('SHACL.ttl',data):
    #     send_data_to_fuseki(fuseki_url, dataset_name, data)

    # collect user preferences
    # user_prefs = collect_user_preferences()
    # print(user_prefs)
    # # create user preferences ttl file
    # rdf_graph= create_rdf_graph(user_prefs)
    # # validate user preferences
    # if shacl_validation('SHACL.ttl',user_prefs):
    #     send_data_to_fuseki(fuseki_url, "pref", rdf_graph, user_prefs['name'])

    now = datetime.datetime.now()
    rank_by = 'distance'  # Default ranking
    if len(sys.argv) < 2:
        print("Usage: python main.py [preference URI]")
        return

    preference_uri = sys.argv[1]
    user_prefs = fetch_user_preferences(preference_uri)
    print(user_prefs)
    # preferences_uri = "pref-charpenay.ttl"
    # preferences_uri = "pref-alex.ttl"
    # user_prefs = fetch_user_preferences(preferences_uri)
    query_restaurants(fuseki_url, dataset_name, now, user_prefs['lat'], user_prefs['lon'], user_prefs['max_distance'], user_prefs['max_price'], rank_by)

    # to launch pref : python3 main.py http://localhost:3030/pref/data?graph=http://example.org/pref-alex
if __name__ == "__main__":
    main()

# ################################# #
# if len(sys.argv) < 7:
#     print("Usage: python main.py <date> <time> <latitude> <longitude> <max_distance_km> <max_price> [--rank-by distance|price]")
#     sys.exit(1)

# date_str, time_str, user_lat, user_lon, max_distance, max_price = sys.argv[1:7]
# if len(sys.argv) == 8:
#     rank_by = sys.argv[7] if sys.argv[7] in ['distance', 'price'] else 'distance'
# user_latitude = 44.8345933 # user's latitude
# user_longitude = -0.5753607  # user's longitude
# max_distance_km = 10  # Maximum distance in kilometers
# price = 114.00  # Maximum price in euros
# date_time = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
# query_restaurants(fuseki_url, dataset_name, date_time, float(user_lat), float(user_lon), float(max_distance), float(max_price), rank_by)
# pour test avec tes données que tu choisis sinon tu enleve le sys.argv si tu veux les utilsier en brute
# python main.py 2023-03-15 14:00 44.8345933 -0.5753607 10 15.00 --rank-by price
# ################################# #