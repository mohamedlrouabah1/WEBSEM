# Semantic Web Project - Delivery Food App

## Description

This project aims to collect restaurants information by web scraping their web pages on the 'coopcycle.org' domain in order to expose them in a triple store database. The collected data is validated against a SHACL validation graph to ensure the consistency of the database. The database is then used in the application to provide restaurant information based on filters set by the user, using a SPARQL query. These filters represent the user's preferences and can also be saved in the database, formatted as a Turtle graph.

## Features

- Collect restaurant data from Coopcycle website
- Validate collected data against SHACL validation graph
- Store data in a triple store database (Jena Fuseki)
- Query the database using SPARQL to get restaurant information based on user preferences
- Save user preferences as a Turtle graph
- Command Line Interface (CLI) for interacting with the application
- Web User Interface (WebUI) for a user-friendly experience

## Installation

1. Clone the repository:
git clone https://github.com/mohamedlrouabah1/WEBSEM/

2. Navigate to the project directory:
cd semantic-web-project

3. Create a virtual environment (recommended):
python3 -m venv venv

4. Activate the virtual environment:
source venv/bin/activate  # On Windows, use venv\Scripts\activate

5. Install the required dependencies:
pip install -r requirements.txt

## Usage

### Command Line Interface (CLI)

Run the following command to see the available CLI options:
python foodies/main.py --help

The CLI supports the following modes:

- `collect`: Initialize, scrape Coopcycle, and populate the triple store database.
- `query`: Query the triple store database.
- `describe`: Gather user preferences and upload them to the database.
- `server`: Launch the Flask server for the WebUI.

### Web User Interface (WebUI)

To start the Flask server for the WebUI, run:
python foodies/main.py -m server
