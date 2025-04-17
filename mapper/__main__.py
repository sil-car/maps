import argparse
import sys
from . import __config__
from . import maps
from .config import years


def main():
    parser = argparse.ArgumentParser(prog='mapper')
    parser.add_argument(
        '--by-year', action='store_true',
        help='create map showing translation project status for each year',
    )
    parser.add_argument(
        '--by-year-diff', action='store_true',
        help='create map showing translation project status for each year with changes highlighted',
    )
    parser.add_argument(
        '--languages', nargs='+',
        help='limit languages shown on map',
    )
    parser.add_argument(
        '--locations', action='store_true',
        help='create map showing language locations',
    )
    parser.add_argument(
        '--names', action='store_true',
        help='show language names',
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
        '--year', nargs=1,
        help='create map showing translation project status by given year',
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
    if args.names:
        __config__.show_names = True
    if args.year:
        __config__.filename = f"car-language-projects-{args.year[0]}"
        __config__.languages = years.get(args.year[0])
        maps.create_population_map()
        sys.exit()
    if args.by_year or args.by_year_diff:
        last_langs = None
        for year, langs in years.items():
            diff = ''
            if last_langs:
                if last_langs == langs:
                    continue
                if args.by_year_diff:
                    diff = '-diff'
                    __config__.prev_languages = last_langs
                    __config__.colors.dot_basic = __config__.colors.sil_blue
            __config__.filename = f"car-language-projects-{year}{diff}"
            __config__.languages = langs
            maps.create_population_map()
            last_langs = langs
        sys.exit()

    if args.locations:
        maps.create_location_map()
    if args.population:
        maps.create_population_map()
    if args.project_status:
        maps.create_project_status_map()


if __name__ == '__main__':
    main()