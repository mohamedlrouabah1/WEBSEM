import rdflib
from rdflib import Namespace, URIRef, Literal, Graph, BNode
from rdflib.namespace import RDF, XSD
import requests

SCHEMA = Namespace('http://schema.org/')
WD = Namespace('http://www.wikidata.org/entity/')

def collect_user_preferences():
    user_name = input("Enter your name: ")
    user_address = input("Enter your address: ")
    user_postal_code = input("Enter your postal code: ")
    user_city = input("Enter your city: ")
    user_country = input("Enter your country: ")
    max_distance = float(input("Enter your maximum distance for a meal (in meters): "))
    longitude = float(input("Enter your longitude: "))
    latitude = float(input("Enter your latitude: "))
    max_price = float(input("Enter your maximum price for a meal (in EUR): "))
    seller_url = input("Enter the URL of the seller (restaurant): ")
    item_offered = input("Enter the Wikidata ID of the item offered: ")

    return {
        'name': user_name,
        'address': user_address,
        'postal_code': user_postal_code,
        'city': user_city,
        'country': user_country,
        'max_distance': max_distance,
        'longitude': longitude,
        'latitude': latitude,
        'max_price': max_price,
        'seller_url': seller_url,
        'item_offered': item_offered
    }

def create_rdf_graph(user_prefs):
    g = Graph()

    # User URI
    user_uri = URIRef(f"http://example.org/user/{user_prefs['name'].replace(' ', '_')}")

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
    g.add((geo_within, SCHEMA.geoRadius, Literal(user_prefs['max_distance'], datatype=XSD.decimal)))
    
    # Price specification
    price_spec = BNode()
    g.add((seeks, SCHEMA.priceSpecification, price_spec))
    g.add((price_spec, SCHEMA.maxPrice, Literal(user_prefs['max_price'], datatype=XSD.decimal)))
    g.add((price_spec, SCHEMA.priceCurrency, Literal("EUR", datatype=XSD.string)))

    # Seller and item offered
    g.add((seeks, SCHEMA.seller, URIRef(user_prefs['seller_url'])))
    g.add((seeks, SCHEMA.itemOfferred, WD[user_prefs['item_offered']]))

    return g

def send_data_to_fuseki(fuseki_url, dataset_name, rdf_graph, user_name):
    """
    Send RDF graph to a Jena Fuseki dataset.

    :param fuseki_url: URL of the Jena Fuseki server
    :param dataset_name: Name of the dataset in Fuseki to which data is to be sent
    :param rdf_graph: RDF graph to be sent
    """
    data_insertion_endpoint = f"{fuseki_url}/{dataset_name}/data?graph=http://example.org/user/{user_name}"
    headers = {"Content-Type": "text/turtle"}
    try:
        response = requests.post(data_insertion_endpoint, data=rdf_graph.serialize(format="turtle"), headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            print(f"Data successfully sent to Jena Fuseki.")
        else:
            print(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error occurred while sending data to Fuseki: {e}")        

def fetch_user_preferences(uri):
    g = rdflib.Graph()
    try:
        g.parse(uri, format='ttl')
    except Exception as e:
        print(f"Erreur lors du chargement du fichier: {e}")
        return None

    user_prefs = {
        'lat': None,
        'lon': None,
        'max_price': None,
        'max_distance': None
    }

    for person in g.subjects(RDF.type, SCHEMA.Person):
        # Itérer à travers les préférences de l'utilisateur
        for seeks in g.objects(person, SCHEMA.seeks):
            # Récupérer les spécifications de prix
            for priceSpec in g.objects(seeks, SCHEMA.priceSpecification):
                maxPrice = g.value(priceSpec, SCHEMA.maxPrice)
                user_prefs['max_price'] = float(maxPrice) if maxPrice else None

            # Récupérer les préférences géographiques
            for availableAtOrFrom in g.objects(seeks, SCHEMA.availableAtOrFrom):
                for geoWithin in g.objects(availableAtOrFrom, SCHEMA.geoWithin):
                    geoMidpoint = g.value(geoWithin, SCHEMA.geoMidpoint)
                    if geoMidpoint:
                        lat = g.value(geoMidpoint, SCHEMA.latitude)
                        lon = g.value(geoMidpoint, SCHEMA.longitude)
                        user_prefs['lat'] = float(lat) if lat else None
                        user_prefs['lon'] = float(lon) if lon else None

                    geoRadius = g.value(geoWithin, SCHEMA.geoRadius)
                    user_prefs['max_distance'] = float(geoRadius) if geoRadius else None

    return user_prefs
