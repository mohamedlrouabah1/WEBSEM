from __future__ import annotations
import sys
import json
import requests
from pyshacl import validate
from rdflib import Graph
from tqdm import tqdm

from config import LDP_URL, LDP_HOST, LDP_PORT, TIMEOUT, LDP_DATASETS, SCRAPPED_DATA_FILE
from config import COOPCYCLE_SHACL_FILE
from models.menu import create_menu_graph
class LdpFuseki:
    """
    Use to interact with the Linked Data Platform of the foodies project.
    We chose to use jena-fuseki as our LDP.
    """
    ENDPOINT_DATA=f'{LDP_URL}'
    ENDPOINT_SHACL=f'http://{LDP_HOST}:{LDP_PORT}/preferences/data?graph=http://foodies.org/validation/shacl'

    def __init__(self, update=False):
        """
        Create the required dataset if it does not exist.
        """
        if not update:
            return

        for dataset in LDP_DATASETS:
            response = requests.post(
                f'http://{LDP_HOST}:{LDP_PORT}/$/datasets',
                params={'dbType': 'tdb2', 'dbName': dataset},
                timeout=TIMEOUT
            )

            if response.status_code == 404:
                print(f"Error while creating dataset {dataset}.", file=sys.stderr)
            
        # upload shacl graph inside preferences dataset :
        shacl = Graph()
        shacl.parse(COOPCYCLE_SHACL_FILE, format='ttl')
        response = requests.post(
                    f"{LdpFuseki.ENDPOINT_SHACL}",
                    data=shacl.serialize(format='turtle'),
                    headers={"Content-Type": "text/turtle"},
                    timeout=TIMEOUT
                )
        
        with open(SCRAPPED_DATA_FILE, 'r', encoding="utf-8") as f:
            data = json.load(f)
        self.upload_ldjson(data)
        self.upload_menu()

    def upload_menu(self):
        with open('foodies/data/menus.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        for restaurant_uri, menu_data in data.items():
            g = create_menu_graph(restaurant_uri, menu_data)
            ttl_data = g.serialize(format='turtle')

            # Upload to Fuseki
            LDP_HOST = 'localhost'
            LDP_PORT = '3030'
            LDP_MAIN_DATASET = 'foodies'
            LDP_URL = f"http://{LDP_HOST}:{LDP_PORT}/{LDP_MAIN_DATASET}"
            headers = {"Content-Type": "text/turtle"}
            response = requests.post(
                        f"{LDP_URL}/data?graph={restaurant_uri}",
                        data=ttl_data,
                        headers=headers,
                        timeout=60
                    )
            print(f"Uploading data for {restaurant_uri}")
            print(response.status_code)
            print(response.text)

    def upload_ldjson(self, data:dict[str,dict]) -> bool:
        """
        Send JSON-LD data to a Jena Fuseki dataset.
        """
        headers = {"Content-Type": "application/ld+json"}
        errors = 0

        for restaurant_url,restaurant_ldjson in tqdm(data.items(),desc='Sending data to Fuseki'):
            if restaurant_ldjson is None:
                continue
            if self._validate_ldjson_against_shacl(restaurant_ldjson):
                try:
                    response = requests.post(
                        f"{LdpFuseki.ENDPOINT_DATA}?graph={restaurant_url}",
                        data=json.dumps(restaurant_ldjson),
                        headers=headers, timeout=TIMEOUT
                        )

                    if response.status_code > 250:
                        print(f"Failed to send data for {restaurant_url}.",
                              f"Status code: {response.status_code},",
                              f"Response: {response.text}",
                              file=sys.stderr)

                except requests.RequestException as e:
                    print(f"Error occurred while sending data for {restaurant_url} to Fuseki: {e}")

            else:
                print(f"Data for {restaurant_url} is not valid. Skipping...", file=sys.stderr)
                errors += 1

        return errors == 0


    def _validate_ldjson_against_shacl(self, data:dict) -> bool:
        """
        Validate JSON-LD data against a SHACL shape.

        :param jsonld_data: JSON-LD data to be validated
        :return: Boolean indicating if data is valid
        """
        # Convert JSON-LD to RDF graph
        rdf_graph = Graph()
        rdf_graph.parse(data=data, format='json-ld')

        # Load SHACL shapes
        response = requests.get(LdpFuseki.ENDPOINT_SHACL, timeout=TIMEOUT)
        if response.status_code != 200:
            print("Failed to load SHACL shapes from the URI", file=sys.stderr)
            return False

        shacl_graph = Graph()
        shacl_graph.parse(data=response.text, format='ttl')

        # Validate the RDF graph against SHACL shapes
        conforms, _, results_text = validate(
            rdf_graph, shacl_graph, inference='rdfs', abort_on_first=False
            )

        if not conforms:
            print("Data is not valid according to SHACL shape.", file=sys.stderr)
            print(results_text, file=sys.stderr)

        return conforms
