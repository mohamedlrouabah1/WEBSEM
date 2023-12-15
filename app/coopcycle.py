import json
import requests
import requests
from bs4 import BeautifulSoup
import json
import tqdm

url = 'https://www.coopcycle.org/fr/'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
select_menu = soup.find('select', id='city-dropdown')
# Extraire les valeurs (URLs) des options
coop_urls = [option['value'] for option in select_menu.find_all('option') 
            if option['value'] and option['value'].find('coopcycle.org') != -1]
# Étape 2: Construire les sous-domaines
coop_domains = [url for url in coop_urls]
# discover urls of all subdomains
coop_domains = [url + '/sitemap.xml' for url in coop_domains]
# now get the JSON-LD from each list of each subdomain
for domain in tqdm(coop_domains, desc='Scraping CoopCycle'):
    response = requests.get(domain)
    loc_tag = BeautifulSoup(response.content, 'html.parser').find_all('loc')
    changefreq_tag = BeautifulSoup(response.content, 'html.parser').find_all('changefreq')
    
    for i in range(len(loc_tag)):
        response = requests.get(loc_tag[i].text)
        # print(loc_tag[i].text)
        # print('----------------------------------------')
        soup = BeautifulSoup(response.content, 'html.parser')
        json_ld_script = soup.find('script', {'type': 'application/ld+json'})
        if json_ld_script:
            json_ld = json.loads(json_ld_script.string)
            # print(json.dumps(json_ld, indent=4, sort_keys=True))
            # print('----------------------------------------')
# Fuseki server details
fuseki_url = 'http://localhost:3030'  # Replace with your Fuseki server URL
dataset_name = 'fooddataset'  # Replace with your dataset name in Fuseki
# Endpoint for data insertion into Fuseki
data_insertion_endpoint = f"{fuseki_url}/{dataset_name}/data"
# Headers for sending JSON-LD
headers = {
    "Content-Type": "application/ld+json"
}
# Convert the JSON-LD data to a string
json_dump = json.dumps(json_ld)
# Send the JSON-LD data to Fuseki
response = requests.post(data_insertion_endpoint, data=json_dump, headers=headers)
# Check the response
if response.status_code == 200:
    print("Data successfully sent to Jena Fuseki.")
else:
    print(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")

