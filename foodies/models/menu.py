from __future__ import annotations
import sys
import json
from urllib.parse import quote
import requests
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from config import LDP_URL, TIMEOUT, AUTHORIZATION_HEADER

SCHEMA = Namespace("http://schema.org/")

def encode_uri_component(component):
    """Clean a string to be used as a URI component."""
    return quote(component.replace(" ", "_"), safe='')

def create_menu_graph(restaurant_uri, menu_data):
    """Create a graph for the menu of a restaurant."""
    menu_graph = Graph()
    # restaurant_ref = URIRef(restaurant_uri)

    for category, items in menu_data.items():
        for item in items:
            item_uri = f"{restaurant_uri}/menu/{encode_uri_component(category)}/{encode_uri_component(item['name'])}"
            item_ref = URIRef(item_uri)
            menu_graph.add((item_ref, RDF.type, SCHEMA.MenuItem))
            menu_graph.add((item_ref, SCHEMA.name, Literal(item["name"], datatype=XSD.string)))
            menu_graph.add((item_ref, SCHEMA.description, Literal(item.get("description", ""), datatype=XSD.string)))
            menu_graph.add((item_ref, SCHEMA.price, Literal(item.get("price", "").replace("\u00a0\u20ac", " EUR"), datatype=XSD.string)))

            if item.get("image"):
                menu_graph.add((item_ref, SCHEMA.image, URIRef(item["image"])))

    return menu_graph


def upload_menu(restaurant_uri:str, ttl_data:str):
    """Uploads the given menu turtle graph to the LDP."""
    response = requests.post(
        f"{LDP_URL}/data?graph={encode_uri_component(restaurant_uri)}",
        data=ttl_data,
        headers={
            "Content-Type": "text/turtle",
            **AUTHORIZATION_HEADER,
        },
        timeout=TIMEOUT,
    )

    if response.status_code != 200:
        print(f"Error while uploading menu for {restaurant_uri}.", file=sys.stderr)
        print(response.text, file=sys.stderr)



if __name__ == '__main__':
   with open('foodies/data/menus.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

        for uri, menus in data.items():
            menu_graph = create_menu_graph(uri, menus)
            menu_ttl = menu_graph.serialize(format='turtle')

            # Upload to Fuseki
            LDP_HOST = 'localhost'
            LDP_PORT = '3030'
            LDP_MAIN_DATASET = 'foodies'
            LDP_URL = f"http://{LDP_HOST}:{LDP_PORT}/{LDP_MAIN_DATASET}"
            headers = {"Content-Type": "text/turtle"}
            response = requests.post(
                        f"{LDP_URL}/data?graph={restaurant_uri}",
                        data=ttl_data,
                        headers=headers,
                        timeout=60
                    )
            print(f"Uploading data for {restaurant_uri}")
            print(response.status_code)
            print(response.text)