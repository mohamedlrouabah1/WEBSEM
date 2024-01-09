"""
Define the web scrapper used to get restaurants from CoopCycle.
This file can either be used as a module or as a standalone script.
"""
from __future__ import annotations
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

from coopcycle_scrapper.ldp_fuseki import LdpFuseki

class CoopCycleScrapper:
    """
    Scrapper for CoopCycle.
    Get all subdomains from the main domain and get all restaurants from each subdomain.
    """
    SKIPPED_URL = ['/a-propos', '/about', '/about-us', '/uber-uns', '/acerca-de',
                   '/su-di-noi', '/sobre-nosotros', '/o-nas','/riguardo-a-noi']

    MAIN_DOMAIN = 'https://coopcycle.org/fr/'

    SAVE_PATH = 'foodies/data/collect.json'

    def __init__(self):
        self.session = requests.Session()
        self.subdomains = self._get_subdomains()
        self.ldp = LdpFuseki()

    def run(self):
        """Main entry point for the scrapper"""
        ldjson_str = self.scrap_restaurants_jsonld()
        ldjson = json.loads(ldjson_str)
        self.ldp.upload_ldjson(ldjson)


    def scrap_restaurants_jsonld(self) -> str:
        """"Get all restaurants from all subdomains of the main domain"""
        all_data = {}

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(
                            self._extract_subdomain_ld_json,
                            domain, self.session
                            )
                        for domain in self.subdomains]

            for future in tqdm(as_completed(futures),total=len(futures),desc='Scraping CoopCycle'):
                all_data.update(future.result())

        with open(CoopCycleScrapper.SAVE_PATH, 'w', encoding="utf-8") as f:
            json.dump(all_data, f)

        result = json.dumps(all_data)
        return result

    def _get_subdomains(self) -> list[str]:
        """
        Get all subdomains from the main domain

        Returns a list of subdomains
        """
        coopcycle_page = self._fetch_and_parse_html(
            CoopCycleScrapper.MAIN_DOMAIN,
            requests.Session()
            )

        select_menu = coopcycle_page.find('select', id='city-dropdown')
        coop_urls = [
            option['value'] + '/sitemap.xml'
            for option in select_menu.find_all('option')
            if option['value'] and 'coopcycle.org' in option['value']
            ]
        return coop_urls

    def _fetch_and_parse_html(self, url:str, session:requests.Session) -> BeautifulSoup:
        """
        Fetches the given URL and returns a BeautifulSoup object

        Returns None if the request failed
        """
        try:
            response = session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None


    def _extract_subdomain_ld_json(self, domain_sitemap:str, session:requests.Session) -> dict[str, str]:
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
        domain_data = {}
        if domain_sitemap := self._fetch_and_parse_html(domain_sitemap, session):
            loc_tags = domain_sitemap.find_all('loc')
            changefreq_tags = domain_sitemap.find_all('changefreq')

            for loc, changefreq in zip(loc_tags, changefreq_tags):
                if any(skip_word in loc.text for skip_word in CoopCycleScrapper.SKIPPED_URL):
                    continue

                domain_data[loc.text] = self._scrap_ldjson_from_url(loc.text, session)
                # domain_data[loc.text] = {
                #     'changefreq': changefreq.text if changefreq else None,
                #     'json_ld': json_ld
                # }

        return domain_data


    def _scrap_ldjson_from_url(self, url:str, session:requests.Session) -> str:
        '''
        Fetches the given URL and returns the JSON-LD data in the page

        Returns None if the request failed
        '''
        scrapped_page = self._fetch_and_parse_html(url, session)
        if scrapped_page:
            json_ld_script = scrapped_page.find('script', {'type': 'application/ld+json'})
            if json_ld_script:
                json_ld = json.loads(json_ld_script.string)
                return json_ld
        return None


    def _scrap_menu_from_url(self, restaurant_url:str, session:requests.Session) -> dict:
        '''
        Fetches the given URL and returns the menu in the page

        Returns None if the request failed

        else dict of menus with key menu name or default and value a list of items of the menu.
        '''
        menus = {}
        scrapped_page = self._fetch_and_parse_html(restaurant_url, session)
        if not scrapped_page:
            return menus

        menu_wrappers = scrapped_page.find_all('div', class_='restaurant-menu-wrapper')

        for menu_wrapper in menu_wrappers:
            menu_title = "default"
            menus[menu_title] = []

            for child in menu_wrapper.children:
                if child.name == 'h2':
                    menu_title = child.text.strip()
                    menus[menu_title] = []

                elif child.name == 'div':
                    menus[menu_title].append( {
                        'name': child.find(class_='menu-item-name').text, # 'h5'
                        'description': child.find(class_='menu-item-description').text, # 'small'
                        'price': child.find( class_='menu-item-price').text.strip(), # 'span',
                        'image': img_tag['src'] if (img_tag := child.find('img')) else None
                    })

        # save json file for debug
        with open('foodies/data/menus.json', 'w', encoding="utf-8") as f:
            json.dump(menus, f)

if __name__ == '__main__':
    CoopCycleScrapper().run()
