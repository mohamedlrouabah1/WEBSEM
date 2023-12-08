import requests
from bs4 import BeautifulSoup
import json

# Étape 1: Analyser la page pour trouver les noms des coopératives
url = "https://coopcycle.org/fr/"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
# print(soup.prettify())
# Trouvez les éléments HTML contenant les noms des coopératives
# Remarque : Vous devrez identifier la classe ou l'id correct dans le HTML
# coop_names = [element.text for element in soup.find_all('option', id='city-dropdown')]
# print(coop_names)
select_menu = soup.find('select', id='city-dropdown')
# print(select_menu.prettify())
# print(type(select_menu))

# Extraire les valeurs (URLs) des options
coop_urls = [option['value'] for option in select_menu.find_all('option') 
             if option['value'] and option['value'].find('coopcycle.org') != -1]

# Afficher la liste des URLs des coopératives
# for url in coop_urls:
#     print(url)
# Étape 2: Construire les sous-domaines
# base_url = "https://{coop_name}.coopcycle.org" # Modèle de base du sous-domaine
# coop_domains = [base_url.format(coop_name=coop_name.lower()) for coop_name in coop_urls]
coop_domains = [url for url in coop_urls]
# discover urls of all subdomains
coop_domains = [url + '/sitemap.xml' for url in coop_domains]
# print(coop_domains)

# now get the JSON-LD from each list of each subdomain
for domain in coop_domains:
    response = requests.get(domain)
    loc_tag = BeautifulSoup(response.content, 'html.parser').find_all('loc')
    changefreq_tag = BeautifulSoup(response.content, 'html.parser').find_all('changefreq')
    # print(loc_tag)
    # print(changefreq_tag)
    
    for i in range(len(loc_tag)):
        response = requests.get(loc_tag[i].text)
        soup = BeautifulSoup(response.content, 'html.parser')
        json_ld_script = soup.find('script', {'type': 'application/ld+json'})
        if json_ld_script:
            json_ld = json.loads(json_ld_script.string)
            print(json.dumps(json_ld, indent=4, sort_keys=True))
        break
            




# Étape 3: Récupérer le JSON-LD de chaque coopérative
# for domain in coop_domains:
#     response = requests.get(domain)
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Analyser pour trouver le JSON-LD
#     # Cela suppose que le JSON-LD est dans une balise <script> de type application/ld+json
#     json_ld_script = soup.find('script', {'type': 'application/ld+json'})
#     if json_ld_script:
#         json_ld = json.loads(json_ld_script.string)
#         print(json_ld)  # Afficher ou traiter le JSON-LD
