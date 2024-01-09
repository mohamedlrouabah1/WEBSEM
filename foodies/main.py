from __future__ import annotations
from foodies_parser import parse_command_line_arguments
from modes import collect, query, describe, server


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
        query(args)
    elif args.mode == 'describe':
        describe(args.fetch)
    elif args.mode == 'server':
        server()


if __name__ == '__main__':
    main()
