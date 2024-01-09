import argparse
import subprocess
from datetime import datetime

from coopcycle_scrapper.scrapper import CoopCycleScrapper
from coopcycle_scrapper.ldp_fuseki import LdpFuseki
from controllers.routes import query_restaurants
from models.describe import describe_user_preferences
from models.menu import create_menu_graph, upload_menu

def parse_command_line_arguments() -> argparse.Namespace:
    """
    Define the command line arguments for the main program.
    """
    parser = argparse.ArgumentParser(
        prog='foodies',
        description='M2 Semantic Web project : food delivery application'
    )

    parser.add_argument(
        '-m', '--mode',
        choices=['collect', 'query', 'describe', 'server'],
        default='query',
        help='The mode to run the program in.'
    )

    ## Collect mode

    parser.add_argument(
        '-i', '--init-fuseki',
        action='store_true',
        help='Initialize Fuseki datasets and shacl validation graph.'
    )

    parser.add_argument(
        '-u', '--upload',
        action='store_true',
        help='Upload scrapped data to Fuseki.'
    )

    ## Query mode
    now = datetime.now()

    parser.add_argument(
        '-d', '--day-of-week',
        default=now.strftime("%A"),
        help='The day of the delivery.'
    )

    parser.add_argument(
        '-t', '--time',
        default=now.strftime("%H:%M"),
        help='The time of the delivery in format : %H:%M.'
    )

    parser.add_argument(
        '-lat', '--latitude',
        default=None,
        help='The latitude of the user.'
    )

    parser.add_argument(
        '-lon', '--longitude',
        default=None,
        help='The longitude of the user.'
    )

    parser.add_argument(
        '-dist', '--distance',
        default=1000,
        help='The maximum distance from the user.'
    )

    parser.add_argument(
        '-p', '--price',
        default=114.00,
        help='The maximum price of the delivery.'
    )

    parser.add_argument(
        '-type', '--type-of-food',
        help='The type of food wanted.'
    )

    parser.add_argument(
        '-r', '--rank-by',
        choices=['distance', 'price'],
        default='distance',
        help='The ranking criteria.'
    )

    parser.add_argument(
        '-fetch', '--fetch',
        help='''
        A URI to a turtle graph.
        mode query:
        The URI to fetch the user preferences from.
        mode describe:
        The URI to fetch a coopcycle member from.
        '''
    )

    return parser.parse_args()


def collect(upload_to_fuseki:bool, init_fuseki:bool, uri:str=None):
    """
    Collect data from CoopCycle or a given URI and upload it to Fuseki.
    """

    if init_fuseki:
        print("Initializing Fuseki datasets and shacl validation graph.")
        LdpFuseki(update=True)

    scrapper = CoopCycleScrapper(upload_to_fuseki)

    if uri:
        print(f"Collecting data from {uri}")
        ldjson = scrapper.scrap_restaurant_from_url(uri)
        scrapper.ldp.upload_ldjson(ldjson) # auto validated agains shacl

        menus = scrapper.scrap_menu_from_url(uri)
        menus_graph = create_menu_graph(menus)
        upload_menu(menus_graph)

    else:
        print("Collecting data from CoopCycle.")
        scrapper.run()



def main():
    """
    Main program.
    """
    args = parse_command_line_arguments()

    print('Bienvenue sur foodies !')
    print('Vous avez sélectionné le mode :', args.mode)
    print("Lancez le programme avec -h pour obtenir plus d'informations sur les arguments.")


    if args.mode == 'collect':
        collect(args.upload, args.init_fuseki, args.fetch)

    elif args.mode == 'query':
        # display all arguments selected for the query mode pass to the query_restaurant function
        print("Querying restaurants with the following arguments :")
        print("\t- Day of week :", args.day_of_week)
        print("\t- Time :", args.time)
        print("\t- Latitude :", args.latitude)
        print("\t- Longitude :", args.longitude)
        print("\t- Distance :", args.distance)
        print("\t- Price :", args.price)
        print("\t- Rank by :", args.rank_by)
        print("\t- Type of food :", args.type_of_food)
        query_restaurants(
            float(args.latitude) if args.latitude else None,
            float(args.longitude) if args.longitude else None,
            float(args.distance) if args.distance else None,
            args.time, args.day_of_week,
            float(args.price), args.rank_by
        )

    elif args.mode == 'describe':
        describe_user_preferences(args.fetch)

    elif args.mode == 'server':
        print("Starting the server.")
        try:
            subprocess.run(['python', 'foodies/app.py'], check=True)
            print("Server started.")

        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de app.py : {e}")


if __name__ == '__main__':
    main()