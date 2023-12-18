import rdflib
from rdflib.namespace import RDF, FOAF

def fetch_user_preferences(uri):
    g = rdflib.Graph()
    g.parse(uri, format='ttl')

    user_prefs = {
        'lat': None,
        'lon': None,
        'max_price': None,
        'max_distance': None
    }

    for person in g.subjects(RDF.type, rdflib.URIRef("http://schema.org/Person")):
        # Fetch the geographic location
        for geo in g.objects(person, rdflib.URIRef("http://schema.org/availableAtOrFrom")):
            for geoMidpoint in g.objects(geo, rdflib.URIRef("http://schema.org/geoMidpoint")):
                lat = g.value(geoMidpoint, rdflib.URIRef("http://schema.org/latitude"))
                lon = g.value(geoMidpoint, rdflib.URIRef("http://schema.org/longitude"))
                user_prefs['lat'] = float(lat) if lat else None
                user_prefs['lon'] = float(lon) if lon else None

            # Fetch the radius if available
            radius = g.value(geo, rdflib.URIRef("http://schema.org/geoRadius"))
            user_prefs['max_distance'] = float(radius) if radius else None

        # Fetch the max price
        for priceSpec in g.objects(person, rdflib.URIRef("http://schema.org/priceSpecification")):
            maxPrice = g.value(priceSpec, rdflib.URIRef("http://schema.org/maxPrice"))
            user_prefs['max_price'] = float(maxPrice) if maxPrice else None

    return user_prefs