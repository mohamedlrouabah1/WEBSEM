from app import app
from flask import render_template, jsonify
from rdflib import Graph, Literal, URIRef, RDF
from rdflib.namespace import XSD, FOAF, DCTERMS

# Import other necessary modules

@app.route('/')
def index():
    rdf_graph = Graph()

    # Creating dummy data
    pizza = URIRef("http://example.org/food/Pizza")
    burger = URIRef("http://example.org/food/Burger")

    # Add triples using store's add() method.
    rdf_graph.add((pizza, RDF.type, URIRef("http://example.org/type/FoodItem")))
    rdf_graph.add((pizza, FOAF.name, Literal("Pizza", datatype=XSD.string)))
    rdf_graph.add((pizza, DCTERMS.description, Literal("Delicious cheese pizza", datatype=XSD.string)))

    rdf_graph.add((burger, RDF.type, URIRef("http://example.org/type/FoodItem")))
    rdf_graph.add((burger, FOAF.name, Literal("Burger", datatype=XSD.string)))
    rdf_graph.add((burger, DCTERMS.description, Literal("Juicy beef burger", datatype=XSD.string)))

    # Serialize the graph to JSON-LD format
    data = rdf_graph.serialize(format="json-ld")
    return render_template('index.html', data=data)


# Additional routes for your application
@app.route('/api/data')
def get_data():
    # Logic to get data (e.g., from RDF store or SPARQL queries)
    data = {'message': 'Data fetched successfully'}
    return jsonify(data)

