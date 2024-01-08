"""
Define the web scrapper used to get restaurants from CoopCycle.
This file can either be used as a module or as a standalone script.
"""

class CoopCycleScrapper:
    """
    Scrapper for CoopCycle.
    Get all subdomains from the main domain and get all restaurants from each subdomain.
    """

    def __init__(self, url):
        self.url = url

    def run(self):
        pass

    def get_restaurants(self):
        pass



if __name__ == '__main__':
    CoopCycleScrapper('https://coopcycle.org/fr/').run()
