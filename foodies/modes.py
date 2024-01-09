from __future__ import annotations
import os
import sys
import subprocess
from argparse import Namespace
from coopcycle_scrapper.scrapper import CoopCycleScrapper
from coopcycle_scrapper.ldp_fuseki import LdpFuseki
from models.query import query_restaurants
from models.describe import describe_user_preferences
from models.menu import create_menu_graph, upload_menu

def collect(upload_to_fuseki:bool, init_fuseki:bool, uri:str=None):
    """
    Collect data from CoopCycle or a given URI and upload it to Fuseki.
    """

    if init_fuseki:
        print("Initializing Fuseki datasets and shacl validation graph.")
        LdpFuseki(update=True)

    scrapper = CoopCycleScrapper(upload_to_fuseki)

    if uri:
        print(f"Collecting data from {uri}")
        ldjson = scrapper.scrap_restaurant_from_url(uri, scrapper.session)
        scrapper.ldp.upload_ldjson(ldjson) # auto validated agains shacl

        menus = scrapper.scrap_menu_from_url(uri, scrapper.session)
        menus_graph = create_menu_graph(uri, menus)
        upload_menu(uri, menus_graph)

    else:
        print("Collecting data from CoopCycle.")
        scrapper.run()


def query(args:Namespace) -> list:
    """Search for a delivery service given the user input."""
    # display all arguments selected for the query mode pass to the query_restaurant function
    print("Querying restaurants with the following arguments :")
    print("\t- Day of week :", args.day_of_week)
    print("\t- Time :", args.time)
    print("\t- Latitude :", args.latitude)
    print("\t- Longitude :", args.longitude)
    print("\t- Distance :", args.distance)
    print("\t- Price :", args.price)
    print("\t- Rank by :", args.rank_by)
    print("\t- Type of food :", args.type_of_food)
    return query_restaurants(
        float(args.latitude) if args.latitude else None,
        float(args.longitude) if args.longitude else None,
        float(args.distance) if args.distance else None,
        args.time, args.day_of_week,
        float(args.price), args.rank_by
    )

def describe(uri:str):
    """Ask or fetch user preferences and upload them on the ldp."""
    return describe_user_preferences(uri)

def server():
    """
    Launch the flask server.
    """
    print("Starting the server.")
    try:
        # get the path of the python exe
        executable = os.path.abspath(sys.executable)
        subprocess.run([executable, 'foodies/app.py'], check=True)
        print("Server started.")

    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de app.py : {e}")