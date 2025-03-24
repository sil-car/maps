import argparse
from . import __config__
from . import maps


def main():
    parser = argparse.ArgumentParser(prog='mapper')
    parser.add_argument(
        '--languages', nargs='+',
        help='limit languages shown on map',
    )
    parser.add_argument(
        '--locations', action='store_true',
        help='create map showing language locations',
    )
    parser.add_argument(
        '--population', action='store_true',
        help='create map showing language population relative sizes',
    )
    parser.add_argument(
        '--project-status', action='store_true',
        help='create map showing translation project status by color',
    )
    parser.add_argument(
        'FILENAME', nargs='?',
        help="specify output filename [optional]",
    )
    args = parser.parse_args()

    if args.FILENAME:
        __config__.filename = args.FILENAME
    if args.languages:
        __config__.languages = args.languages
    if args.locations:
        maps.create_location_map()
    if args.population:
        maps.create_population_map()
    if args.project_status:
        maps.create_project_status_map()


if __name__ == '__main__':
    main()