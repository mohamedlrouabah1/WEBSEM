import requests
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from tqdm import tqdm

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

def launch_scrap(url):
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

    with open('coopcycle.json', 'w') as file:
        json.dump(all_data, file)
    
    return all_data