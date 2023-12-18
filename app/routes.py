from app import app
from flask import render_template, jsonify, request
from rdflib import Graph, Literal, URIRef, RDF
from rdflib.namespace import XSD, FOAF, DCTERMS
from .models import FoodItem, Restaurant, Customer
from .sparql import execute_sparql_query, update_customer_preferences

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

@app.route('/updatePreferences', methods=['POST'])
def update_preferences():
    customer_name = request.form['name']
    new_preferences = request.form['preferences']  # This should be formatted correctly
    update_customer_preferences(customer_name, new_preferences)
    return jsonify({"message": "Preferences updated successfully."})

@app.route('/listBusinesses', methods=['GET'])
def list_businesses():
    # Example SPARQL query
    query = """ 
    PREFIX schema: <http://schema.org/>
    SELECT ?business WHERE {
        ?business a schema:Restaurant.
    }
    """
    results = execute_sparql_query(query)
    businesses = [str(result['business']) for result in results]
    return jsonify({"businesses": businesses})