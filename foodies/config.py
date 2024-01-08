"""
Configuration file for the foodies application.
"""
from os import getenv

LDP_TYPE=getenv('LDP_TYPE', 'Jena')
LDP_HOST=getenv('LDP_HOST', 'localhost')
LDP_PORT=getenv('LDP_PORT', '3030')
LDP_DATASET=getenv('LDP_DATASET', 'foodies')

LDP_URL = f"http://{LDP_HOST}:{LDP_PORT}/{LDP_DATASET}"


TIMEOUT=20
