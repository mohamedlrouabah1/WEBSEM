"""
Transform the json file of scrapped menu items into a
turtle graph
"""
from __future__ import annotations
import requests
import json
from rdflib import Namespace, URIRef, Literal, Graph
from rdflib.namespace import RDF, XSD
# from config import LDP_URL, TIMEOUT


SCHEMA = Namespace('http://schema.org/')
WD = Namespace('http://www.wikidata.org/entity/')

def create_restaurants_menus_graph(menus:dict) -> Graph:
    g = Graph()
    for uri, menus in menus.items():
        restaurant_uri = URIRef(uri)
        if menus is None:
            continue

        for menu_name, items in menus.items():
            if items is None:
                continue

            menu_uri = URIRef(f"{uri}/menu/{menu_name.replace(' ', '_')}")
            g.add((restaurant_uri, SCHEMA.hasMenu, menu_uri))

            for item in items:
                if item['name'] is None:
                    continue
                name = item['name'].replace(' ', '_').replace('\"', '')
                item_uri = URIRef(f"{menu_uri}/item/{name}")
                g.add((item_uri, RDF.type, SCHEMA.MenuItem))
                g.add((item_uri, SCHEMA.name, Literal(item['name'], datatype=XSD.string)))
                g.add((item_uri, SCHEMA.description, Literal(item['description'], datatype=XSD.string)))
                price = rf'{item["price"]}'
                g.add((item_uri, SCHEMA.price, Literal(price, datatype=XSD.string)))
                g.add((menu_uri, SCHEMA.hasMenuItem, item_uri))

    # save graph for debug
    g.serialize('foodies/data/menus.ttl', format='turtle')

    return g

if __name__ == '__main__':
    with open('foodies/data/menus.json', 'r', encoding="utf-8") as f:
        menus = json.load(f)
        create_restaurants_menus_graph(menus)

    #upload ttl to fuseki
    LDP_HOST = 'localhost'
    LDP_PORT = '3030'
    LDP_MAIN_DATASET = 'foodies'
    LDP_URL = f"http://{LDP_HOST}:{LDP_PORT}/{LDP_MAIN_DATASET}"
    with open('foodies/data/menus.ttl', 'r', encoding="utf-8") as f:
        data = f.read()
        headers = {"Content-Type": "text/turtle"}
        response = requests.post(
                    f"{LDP_URL}/data?graph=http://foodies.org/menus",
                    data=data,
                    headers=headers,
                    timeout=60
                )
        print(response.status_code)
        print(response.text)