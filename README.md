# Foodies

## Installation

```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

## Utilisation

See the help of the CLI for more information

```bash
venv/Scripts/python.exe foodies/main.py -h
```

When launch on server mode the UI is availible at port 5000

## Random notes

### Create a jena dataset

```bash
curl -X POST -u user:pwd -d "dbName=test-3&dbType=mem" https://dsc2-sw-food-delivery-b3a7e3e908fb.herokuapp.com/$/datasets
``
