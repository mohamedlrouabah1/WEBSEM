from pyshacl import validate
import pyshacl
from rdflib import XSD, Graph, Namespace, RDF, Literal, URIRef

# Namespaces
SCHEMA = Namespace("http://schema.org/")

# Define the FoodItem model
class FoodItem:
    def __init__(self, name, description, price, category):
        self.name = name
        self.description = description
        self.price = price
        self.category = category

    def to_rdf(self, graph):
        food_item_uri = URIRef(f"http://example.org/food/{self.name.replace(' ', '_')}")
        graph.add((food_item_uri, RDF.type, SCHEMA.FoodItem))
        graph.add((food_item_uri, SCHEMA.name, Literal(self.name)))
        graph.add((food_item_uri, SCHEMA.description, Literal(self.description)))
        graph.add((food_item_uri, SCHEMA.price, Literal(self.price, datatype=XSD.decimal)))
        graph.add((food_item_uri, SCHEMA.category, Literal(self.category)))

# Define the Restaurant model with SHACL validation
class Restaurant:
    def __init__(self, name, address, menuItems, ratings):
        self.name = name
        self.address = address
        self.menuItems = menuItems
        self.ratings = ratings

    def to_rdf(self, graph):
        restaurant_uri = URIRef(f"http://example.org/restaurant/{self.name.replace(' ', '_')}")
        graph.add((restaurant_uri, RDF.type, SCHEMA.Restaurant))
        graph.add((restaurant_uri, SCHEMA.name, Literal(self.name)))
        graph.add((restaurant_uri, SCHEMA.address, Literal(self.address)))
        # Add menuItems and ratings as needed

# Define the Customer model
class Customer:
    def __init__(self, name, preferences):
        self.name = name
        self.preferences = preferences

    def to_rdf(self, graph):
        customer_uri = URIRef(f"http://example.org/customer/{self.name.replace(' ', '_')}")
        graph.add((customer_uri, RDF.type, SCHEMA.Person))
        graph.add((customer_uri, SCHEMA.name, Literal(self.name)))
        graph.add((customer_uri, SCHEMA.preferences,Literal(self.preferences)))
        # graph.add((customer_uri, SCHEMA.rating, Literal(self.rating, datatype=XSD.integer)))
        # graph.add((customer_uri, SCHEMA.review, Literal(self.review)))
            
    def update_preferences(self, new_preferences):
        self.preferences = new_preferences
        # Update RDF graph if necessary

def validate_graph_with_shacl(graph):
    # Define your SHACL shapes here or load them from a file
    shapes_graph = """
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix schema: <http://schema.org/> .

    <#RestaurantShape> a sh:NodeShape;
        sh:targetClass schema:Restaurant;
        sh:property [
            sh:path schema:name;
            sh:datatype XSD:string;
            sh:minCount 1;
        ].
    """

    shapes_graph = Graph().parse(data=shapes_graph, format='turtle')
    conforms, v_graph, v_text = pyshacl.validate(graph, shacl_graph=shapes_graph)
    if not conforms:
        print("Validation Error:", v_text)
    return conforms