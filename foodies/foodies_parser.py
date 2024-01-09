import argparse
from datetime import datetime


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
