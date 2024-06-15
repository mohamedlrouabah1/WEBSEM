"""
Define the cache configuration for foodies app.
"""
from flask_caching import Cache


cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_THRESHOLD': 500,
    'CACHE_MAXSIZE': 32 * 1024 * 1024
    })

CACHE_DEFAULT_TIMEOUT = 30


CACHE_CONFIG = config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": CACHE_DEFAULT_TIMEOUT,
    'SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS': True,
}
