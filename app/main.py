
import datetime
import json
import sys
import requests

from scrap import launch_scrap
from coopcycle import send_data_to_fuseki
from sparql import query_restaurants_open_at, query_restaurants
from preferencies import fetch_user_preferences
def main():
    # url = "https://coopcycle.org/fr/"
    # data = launch_scrap(url)
    # load json file
    # data = json.load(open('coopcycle.json'))
    fuseki_url = "http://localhost:3030"
    dataset_name = "foodies"
    # send_data_to_fuseki(fuseki_url, dataset_name, data)
    # query_restaurants_open_at(fuseki_url, dataset_name, date)
    
    if len(sys.argv) < 7:
        print("Usage: python main.py <date> <time> <latitude> <longitude> <max_distance_km> <max_price> [--rank-by distance|price]")
        sys.exit(1)

    date_str, time_str, user_lat, user_lon, max_distance, max_price = sys.argv[1:7]
    rank_by = 'distance'  # Default ranking
    if len(sys.argv) == 8:
        rank_by = sys.argv[7] if sys.argv[7] in ['distance', 'price'] else 'distance'
    # user_latitude = 44.8345933 # user's latitude
    # user_longitude = -0.5753607  # user's longitude
    # max_distance_km = 10  # Maximum distance in kilometers
    # price = 114.00  # Maximum price in euros
    # date_time = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    now = datetime.datetime.now()
    
    preferences_uri = "pref-charpenay.ttl" 
    user_prefs = fetch_user_preferences(preferences_uri)
    query_restaurants(fuseki_url, dataset_name, now, user_prefs['lat'], user_prefs['lon'], user_prefs['max_distance'], user_prefs['max_price'], rank_by)

    # query_restaurants(fuseki_url, dataset_name, date_time, float(user_lat), float(user_lon), float(max_distance), float(max_price), rank_by)
    # pour test avec tes données que tu choisis sinon tu enleve le sys.argv si tu veux les utilsier en brute
    # python main.py 2023-03-15 14:00 44.8345933 -0.5753607 10 15.00 --rank-by price
if __name__ == "__main__":
    main()