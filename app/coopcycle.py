import json
import requests

def send_data_to_fuseki(fuseki_url, dataset_name, json_ld_data):
    """
    Send JSON-LD data to a Jena Fuseki dataset.

    :param fuseki_url: URL of the Jena Fuseki server
    :param dataset_name: Name of the dataset in Fuseki to which data is to be sent
    :param json_ld_data: JSON-LD data to be sent
    """
    data_insertion_endpoint = f"{fuseki_url}/{dataset_name}/data"
    headers = {"Content-Type": "application/ld+json"}

    json_dump = json.dumps(json_ld_data)

    try:
        response = requests.post(data_insertion_endpoint, data=json_dump, headers=headers)
        if response.status_code == 200:
            print("Data successfully sent to Jena Fuseki.")
        else:
            print(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error occurred while sending data to Fuseki: {e}")
