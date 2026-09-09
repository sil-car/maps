import csv
from . import __config__


def get_cag_lgs_info_csv(filtered_isos=None):
    x = []
    y = []
    names = []
    populations = []
    stages = []

    csv_file = __config__.data_dir / 'CAG_Lgs_Info-CAR.csv'
    with csv_file.open() as f:
        r = csv.reader(f)
        ct = 0
        for row in r:
            # print(f"{row=}")
            iso = row[3].strip('(').strip(')')
            if ct == 0:
                # skip header row
                ct += 1
                continue
            # Skip rows whose LAT and LON are empty.
            try:
                yi = float(row[1])
                xi = float(row[2])
            except ValueError:
                continue
            # Skip map alignment rows.
            if __config__.show_control_points is False and row[0].endswith('tip'):
                continue
            # Skip excluded rows, if defined.
            if filtered_isos and iso not in filtered_isos:
                continue
            # Skip excluded rows, if defined (alternative method).
            if isinstance(__config__.languages, (tuple, list)) and iso not in __config__.languages:
                continue
            names.append(row[0])
            x.append(xi)
            y.append(yi)
            try:
                populations.append(int(row[11]))
            except ValueError:
                populations.append(0)
            stages.append(row[4])
    return x, y, names, populations, stages
