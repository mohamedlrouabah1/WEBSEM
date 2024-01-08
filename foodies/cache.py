"""
Define the cache configuration for foodies app.
"""
from flask_caching import Cache


cache = Cache()

CACHE_DEFAULT_TIMEOUT = 30


CACHE_CONFIG = config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": CACHE_DEFAULT_TIMEOUT,
    'SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS': True,
}
