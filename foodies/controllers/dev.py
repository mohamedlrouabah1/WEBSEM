import json
from flask import Blueprint, render_template, jsonify

from coopcycle_scrapper.ldp_fuseki import LdpFuseki
from coopcycle_scrapper.scrapper import CoopCycleScrapper

dev_bp = Blueprint('dev', __name__, url_prefix='/dev')

@dev_bp.route('/')
def dev_page():
    """Access to the Debbug page of the application."""
    return render_template('dev.html')

@dev_bp.route('/collect-data', methods=['POST'])
def collect_data_route():
    """
    Launch the webscrapping of CoopCycle's website
    and save the data in a json file.
    """
    CoopCycleScrapper().run()
    result = jsonify({'message': 'Données collectées avec succès'})
    return render_template('dev.html' , result=result)


@dev_bp.route('/send-to-fuseki', methods=['POST'])
def send_to_fuseki():
    """Upload json files to the linked data platform."""
    try:
        with open("foodies/data/collect.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        LdpFuseki().upload_ldjson(data)
        return render_template('dev.html' , result=jsonify({'message': 'Données envoyées avec succès'}))

    except Exception as e:
        return render_template(
            'dev.html' ,
            result=jsonify({'message': f'Erreur lors de la lecture du fichier collect.json : {e}'})
            )