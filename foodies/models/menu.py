from __future__ import annotations
import json
import requests
import sys
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from urllib.parse import quote
from config import LDP_URL, TIMEOUT, LDP_HOST, LDP_PORT

SCHEMA = Namespace("http://schema.org/")

def encode_uri_component(component):
    """Clean a string to be used as a URI component."""
    return quote(component.replace(" ", "_"), safe='')

def create_menu_graph(restaurant_uri, menu_data):
    """Create a graph for the menu of a restaurant."""
    g = Graph()
    # restaurant_ref = URIRef(restaurant_uri)

    for category, items in menu_data.items():
        for item in items:
            item_uri = f"{restaurant_uri}/menu/{encode_uri_component(category)}/{encode_uri_component(item['name'])}"
            item_ref = URIRef(item_uri)
            g.add((item_ref, RDF.type, SCHEMA.MenuItem))
            g.add((item_ref, SCHEMA.name, Literal(item["name"], datatype=XSD.string)))
            g.add((item_ref, SCHEMA.description, Literal(item.get("description", ""), datatype=XSD.string)))
            g.add((item_ref, SCHEMA.price, Literal(item.get("price", "").replace("\u00a0\u20ac", " EUR"), datatype=XSD.string)))

            if item.get("image"):
                g.add((item_ref, SCHEMA.image, URIRef(item["image"])))

    return g


def upload_menu(restaurant_uri:str, ttl_data:str):
    """Uploads the given menu turtle graph to the LDP."""
    headers = {"Content-Type": "text/turtle"}
    response = requests.post(
        f"{LDP_URL}/{encode_uri_component(restaurant_uri)}/data",
        data=ttl_data,
        headers=headers,
        timeout=TIMEOUT,
    )

    if response.status_code != 200:
        print(f"Error while uploading menu for {restaurant_uri}.", file=sys.stderr)
        print(response.text, file=sys.stderr)

    

if __name__ == '__main__':
   with open('foodies/data/menus.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

        for restaurant_uri, menu_data in data.items():
            g = create_menu_graph(restaurant_uri, menu_data)
            ttl_data = g.serialize(format='turtle')

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