"""
Foodies application.
"""
import os
from flask import Flask, send_from_directory
from flask_sitemap import Sitemap


from cache import cache, CACHE_CONFIG
from controllers.routes import main_bp
from controllers.dev import dev_bp
from controllers.user import user_bp

debug = os.getenv('DEBUG', 'True') == 'True'

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['ADDITIONAL_STATIC_FOLDER'] = 'foodies/data'
app.config.from_mapping(CACHE_CONFIG)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

cache.init_app(app)

app.register_blueprint(main_bp, url_prefix='')
app.register_blueprint(user_bp)
if debug:
    app.register_blueprint(dev_bp)

sitemap = Sitemap(app=app)

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    """Serve the favicon.ico file."""
    return app.send_static_file('favicon.ico')

@app.route('/data/<path:filename>')
def additional_static(filename):
    return send_from_directory(app.config['ADDITIONAL_STATIC_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=debug)
