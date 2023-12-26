import requests
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from tqdm import tqdm
from rdflib import Graph
from pyshacl import validate

def fetch_and_parse(url, session):
    '''
    Fetches the given URL and returns a BeautifulSoup object
    
    Returns None if the request failed
    '''
    try:
        response = session.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def process_domain(domain, session):
    '''
    Fetches the sitemap for the given domain and processes each page in the sitemap
    
    Returns a dictionary of JSON-LD data with the URL as the key
    
    Example:
    {
        "https://coopcycle.org/fr/": {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "CoopCycle",
            "url": "https://coopcycle.org/fr/"
        },
        "https://coopcycle.org/fr/about/": {
            "@context": "https://schema.org",
            "@type": "AboutPage",
            "name": "À propos",
            "url": "https://coopcycle.org/fr/about/"
        },
        ...
    }
    '''
    # skip /a-propos dans toute les langues
    skip = ['/a-propos', '/about','/about-us' '/uber-uns', '/acerca-de', '/su-di-noi', '/sobre-nosotros', '/o-nas','/riguardo-a-noi']
    domain_data = {}
    domain_soup = fetch_and_parse(domain, session)
    if domain_soup:
        loc_tags = domain_soup.find_all('loc')
        changefreq_tags = domain_soup.find_all('changefreq')

        for loc, changefreq in zip(loc_tags, changefreq_tags):
            if any(skip_word in loc.text for skip_word in skip):
                continue
            page_soup = fetch_and_parse(loc.text, session)
            if page_soup:
                json_ld_script = page_soup.find('script', {'type': 'application/ld+json'})
                if json_ld_script:
                    json_ld = json.loads(json_ld_script.string)
                    domain_data[loc.text] = json_ld  # Directly assign json_ld
                    # domain_data[loc.text] = {
                    #     'changefreq': changefreq.text if changefreq else None,
                    #     'json_ld': json_ld
                    # }
    return domain_data

def collect(url):
    '''
    Launches the scraping process for the given URL
    
    Scrapes the sitemap for the given URL and all subdomains
    
    Saves the results to a JSON file
    '''
    session = requests.Session()
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    select_menu = soup.find('select', id='city-dropdown')
    coop_urls = [option['value'] + '/sitemap.xml' for option in select_menu.find_all('option') if option['value'] and 'coopcycle.org' in option['value']]

    all_data = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_domain, domain, session) for domain in coop_urls]
        for future in tqdm(as_completed(futures), total=len(futures), desc='Scraping CoopCycle'):
            all_data.update(future.result())

    with open('collect.json', 'w') as file:
        json.dump(all_data, file)
    
    return json.dump(all_data)

def send_data_to_fuseki(fuseki_url, dataset_name, json_ld_data):
    """
    Send JSON-LD data to a Jena Fuseki dataset.

    :param fuseki_url: URL of the Jena Fuseki server
    :param dataset_name: Name of the dataset in Fuseki to which data is to be sent
    :param json_ld_data: JSON-LD data to be sent
    """
    data_insertion_endpoint = f"{fuseki_url}/{dataset_name}/data"
    headers = {"Content-Type": "application/ld+json"}
    for restaurant_url,restaurant_json_data in tqdm(json_ld_data.items(), desc='Sending data to Fuseki'):
        graph_uri = f"{data_insertion_endpoint}?graph={restaurant_url}"
        try:
            response = requests.post(graph_uri, data=json.dumps(restaurant_json_data), headers=headers)
            if response.status_code != 200 or response.status_code != 201:
            #     print(f"Data for {restaurant_url} successfully sent to Jena Fuseki.")
            # else:
                print(f"Failed to send data for {restaurant_url}. Status code: {response.status_code}, Response: {response.text}")
        except requests.RequestException as e:
            print(f"Error occurred while sending data for {restaurant_url} to Fuseki: {e}")

def shacl_validation(jsonld_data):
    """
    Validate JSON-LD data against a SHACL shape.

    :param jsonld_data: JSON-LD data to be validated
    :return: Boolean indicating if data is valid
    """
    # Convert JSON-LD to RDF graph
    rdf_graph = Graph()
    rdf_graph.parse(data=jsonld_data, format='json-ld')

    # Load SHACL shapes
    shacl_shapes_uri = 'http://localhost:3030/preferencies/data?graph=http://foodies.org/validation/shacl'
    response = requests.get(shacl_shapes_uri)
    if response.status_code != 200:
        print("Failed to load SHACL shapes from the URI")
        return False

    shacl_graph = Graph()
    shacl_graph.parse(data=response.text, format='ttl')

    # Validate the RDF graph against SHACL shapes
    conforms, results_graph, results_text = validate(rdf_graph, shacl_graph=shacl_graph, inference='rdfs', abort_on_error=False)
    if conforms:
        print("Data is valid according to SHACL shape.")
    else:
        print("Data is not valid according to SHACL shape.")
        print(results_text)

    return conforms