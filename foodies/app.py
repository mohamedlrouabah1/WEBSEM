"""
Foodies application.
"""
import os
from flask import Flask
from flask_sitemap import Sitemap


from cache import cache, CACHE_CONFIG
from controllers.routes import main_bp


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_mapping(CACHE_CONFIG)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

cache.init_app(app)

app.register_blueprint(main_bp, url_prefix='')
sitemap = Sitemap(app=app)






if __name__ == '__main__':
    debug = os.getenv('DEBUG', 'True') == 'True'
    app.run(debug=debug)
