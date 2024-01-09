from __future__ import annotations
import requests
from rdflib import Namespace, URIRef, Literal, Graph, BNode
from rdflib.namespace import RDF, XSD
from config import LDP_URL, TIMEOUT, LDP_HOST, LDP_PORT

SCHEMA = Namespace('http://schema.org/')
WD = Namespace('http://www.wikidata.org/entity/')

def collect_user_preferences() -> dict:
    """
    CLI interface to collect user preferences.
    """
    preferences = {}

    for key in ('name', 'address', 'postal_code', 'city', 'country', 'seller_url', 'item_offered'):
        preferences[key] = input(f"Enter your {key}: ")

    for key in ('max_distance', 'longitude', 'latitude', 'max_price'):
        preferences[key] = float(input(f"Enter your {key}: "))

    return preferences

def create_rdf_graph(user_prefs:dict) -> Graph:
    """
    Createa an RDF graph from user preferences using rdfLib.
    """
    g = Graph()
    user_uri = URIRef(f"http://foodies.org/user/{user_prefs['name'].replace(' ', '_')}")

    # User details
    g.add((user_uri, RDF.type, SCHEMA.Person))
    g.add((user_uri, SCHEMA.name, Literal(user_prefs['name'], datatype=XSD.string)))

    # Address details
    address = BNode()
    g.add((user_uri, SCHEMA.address, address))
    g.add((address, RDF.type, SCHEMA.PostalAddress))
    g.add((address, SCHEMA.postalCode, Literal(user_prefs['postal_code'], datatype=XSD.string)))
    g.add((address, SCHEMA.addressLocality, Literal(f"{user_prefs['city']}, {user_prefs['country']}", datatype=XSD.string)))
    g.add((address, SCHEMA.streetAddress, Literal(user_prefs['address'], datatype=XSD.string)))

    # Preferences (seeks)
    seeks = BNode()
    g.add((user_uri, SCHEMA.seeks, seeks))

    # Geolocation preferences
    availableAtOrFrom = BNode()
    g.add((seeks, SCHEMA.availableAtOrFrom, availableAtOrFrom))

    geo_within = BNode()
    g.add((availableAtOrFrom, SCHEMA.geoWithin, geo_within))
    g.add((geo_within, RDF.type, SCHEMA.GeoCircle))

    geo_midpoint = BNode()
    g.add((geo_within, SCHEMA.geoMidpoint, geo_midpoint))
    g.add((geo_midpoint, SCHEMA.latitude, Literal(user_prefs['latitude'], datatype=XSD.decimal)))
    g.add((geo_midpoint, SCHEMA.longitude, Literal(user_prefs['longitude'], datatype=XSD.decimal)))
    g.add((geo_within, SCHEMA.geo_radius, Literal(user_prefs['max_distance'], datatype=XSD.decimal)))

    # Price specification
    price_spec = BNode()
    g.add((seeks, SCHEMA.priceSpecification, price_spec))
    g.add((price_spec, SCHEMA.max_price, Literal(user_prefs['max_price'], datatype=XSD.decimal)))
    g.add((price_spec, SCHEMA.priceCurrency, Literal("EUR", datatype=XSD.string)))

    # Seller and item offered
    g.add((seeks, SCHEMA.seller, URIRef(user_prefs['seller_url'])))
    g.add((seeks, SCHEMA.itemOfferred, WD[user_prefs['item_offered']]))

    return g

def send_data_to_fuseki(rdf_graph:Graph, user_name:str) -> None:
    """
    Send RDF graph to a Jena Fuseki dataset.

    :param fuseki_url: URL of the Jena Fuseki server
    :param dataset_name: Name of the dataset in Fuseki to which data is to be sent
    :param rdf_graph: RDF graph to be sent
    """
    try:
        response = requests.post(
            f"{LDP_URL}/data?graph=http://foodies.org/user/{user_name.replace(' ', '_')}",
            data=rdf_graph.serialize(format="turtle"),
            headers={"Content-Type": "text/turtle"},
            timeout=TIMEOUT
            )

        if response.status_code in (200, 201):
            print('Data successfully sent to Jena Fuseki.')
        else:
            print(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")

    except requests.RequestException as e:
        print(f"Error occurred while sending data to Fuseki: {e}")


def fetch_user_preferences(uri_name:str) -> dict:
    """
    Query the Jena LDP for a specific user preferences.
    """
    response = requests.get(
        f"http://{LDP_HOST}:{LDP_PORT}/preferences/data?graph=http://foodies.org/user/{uri_name}",
        timeout=TIMEOUT)

    if response.status_code != 200:
        print("Failed to load SHACL shapes from the URI")
        return False

    g = Graph()
    g.parse(data=response.text, format='ttl')

    user_prefs = {}

    for person in g.subjects(RDF.type, SCHEMA.Person):
        # Itérer à travers les préférences de l'utilisateur
        for seeks in g.objects(person, SCHEMA.seeks):
            # Récupérer les spécifications de prix
            for price_spec in g.objects(seeks, SCHEMA.priceSpecification):
                max_price = g.value(price_spec, SCHEMA.maxPrice)
                user_prefs['max_price'] = float(max_price) if max_price else None

            # Récupérer les préférences géographiques
            for available_at_or_from in g.objects(seeks, SCHEMA.availableAtOrFrom):
                for geo_within in g.objects(available_at_or_from, SCHEMA.geoWithin):
                    geo_midpoint = g.value(geo_within, SCHEMA.geoMidpoint)
                    if geo_midpoint:
                        lat = g.value(geo_midpoint, SCHEMA.latitude)
                        lon = g.value(geo_midpoint, SCHEMA.longitude)

                        user_prefs['lat'] = float(lat) if lat else None
                        user_prefs['lon'] = float(lon) if lon else None


                    geo_radius = g.value(geo_within, SCHEMA.geoRadius)
                    user_prefs['max_distance'] = float(geo_radius) if geo_radius else None

    return user_prefs



def describe_user_preferences(uri:str=None) -> Graph:
    """
    Ask the user to enter their preferences and send them to a Jena Fuseki dataset.
    If an uri is provided, fetch the user preferences from the turtle graph at the uri.
    """
    if uri:
        print(f"Fetching user preferences from {uri}")
        response = requests.get(
            uri,
            headers={'Accept': 'text/turtle'},
            timeout=60
        )
        ref_graph = Graph()
        ref_graph.parse(data=response.text, format='ttl')
        print(ref_graph.serialize(format='turtle').decode('utf-8'))

    else:
        user_prefs = collect_user_preferences()
        rdf_graph = create_rdf_graph(user_prefs)

    print("Verifying graph with shacl and then upload to fuseki.")
    send_data_to_fuseki(rdf_graph, user_prefs['name'])
    print(fetch_user_preferences(user_prefs['name']))
    return rdf_graph


if __name__ == '__main__':
    describe_user_preferences()