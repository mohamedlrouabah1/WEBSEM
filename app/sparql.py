from rdflib import Graph, OWL, URIRef

# Initialize your RDF graph
g = Graph()

# Function to load RDF data into the graph
def load_rdf_data(rdf_data_source):
    g.parse(rdf_data_source, format='turtle')  # Adjust the format as needed

# Function to execute a SPARQL query
def execute_sparql_query(query):
    return g.query(query)

# Example function to find businesses near a given geolocation using SPARQL
def find_nearby_businesses(geolocation):
    query = """
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    SELECT ?business WHERE {
        ?business geo:location ?location .
        FILTER (nearby(?location, """ + geolocation + """))  # Replace with appropriate logic
    }
    """
    return execute_sparql_query(query)

def update_customer_preferences(customer_name, new_preferences):
    # SPARQL Update query logic
    # Ensure new_preferences is in the correct format
    update_query = """
    PREFIX schema: <http://schema.org/>
    DELETE WHERE {
        ?customer schema:preferences ?oldPreferences.
    };
    INSERT {
        ?customer schema:preferences """ + new_preferences + """.
    }
    WHERE {
        ?customer a schema:Person;
                 schema:name '""" + customer_name + """'.
    }
    """
    g.update(update_query)
# Consider owl:sameAs in SPARQL queries
g.namespace_manager.bind("owl", OWL)

