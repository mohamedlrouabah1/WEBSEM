import requests
from models import FoodItem
from rdflib import Graph

def collect_and_convert_data(url):
    response = requests.get(url)
    data = response.json()  # Supposons que la réponse est en JSON

    graph = Graph()
    for item in data:
        food_item = FoodItem(item['name'], item['description'], item['price'], item['category'])
        graph += food_item.to_rdf(graph)  # Ajouter à un graphe RDF

    return graph.serialize(format='turtle')  # Retourner le graphe RDF en format Turtle

# Exemple d'utilisation
url = "https://coopcycle.org/fr/federation/"
rdf_data = collect_and_convert_data(url)
# Envoyez ensuite ces données à Fuseki ici
