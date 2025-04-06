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
            iso = row[3].strip('(').strip(')')
            if ct == 0:
                ct += 1
                continue
            elif row[0].endswith('tip'):
                continue
            if filtered_isos and iso not in filtered_isos:
                continue
            if hasattr(__config__.languages, '__iter__') and iso not in __config__.languages:
                continue
            names.append(row[0])
            try:
                x.append(float(row[2]))
            except ValueError:
                x.append(0)
            try:
                y.append(float(row[1]))
            except ValueError:
                y.append(0)
            try:
                populations.append(int(row[11]))
            except ValueError:
                populations.append(0)
            stages.append(row[4])
    return x, y, names, populations, stages