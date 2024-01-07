import os
from flask import Flask


from controllers.routes import main_bp


app = Flask(__name__, template_folder='templates', static_folder='static')
app.register_blueprint(main_bp, url_prefix='')


app.secret_key = os.environ.get('SECRET_KEY', 'dev')


if __name__ == '__main__':
    debug = os.getenv('DEBUG', 'True') == 'True'
    app.run(debug=debug)