import argparse
from . import maps


def main():
    parser = argparse.ArgumentParser(prog='mapper')
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
    args = parser.parse_args()

    if args.locations:
        maps.create_location_map()
    if args.population:
        maps.create_population_map()
    if args.project_status:
        maps.create_project_status_map()


if __name__ == '__main__':
    main()