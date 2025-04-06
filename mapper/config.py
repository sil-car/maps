import matplotlib.patheffects as path_effects
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path


def define_path_effect(**kwargs):
    return [path_effects.Stroke(**kwargs), path_effects.Normal()]


@dataclass
class Colors:
    """Keep track of color scheme."""
    dot_basic: str = 'white'
    dot: str = 'red'
    unengaged: str = 'red'
    ongoing: str = 'yellow'
    done: str = 'green'
    text: str = 'xkcd:royal blue'


@dataclass
class Geometry:
    """Keep track of geometry preferences."""
    dot_radius_factor: int = 5
    dot_basic_alpha: float = 0.9
    dot_prev_alpha: float = 0.4
    dot_basic_radius_factor: int = 10
    offset_base_image = (20, -100)  # used to align generated images with base image
    offset_location_text = (0, 5)  # text labels for dots on location map
    text_rotation: int = 15


@dataclass
class Config:
    """Store all config for the app."""
    colors: Colors = field(default_factory=Colors)
    filename: str = None
    geometry: Geometry = field(default_factory=Geometry)
    show_names: bool = True
    languages = 'all'
    prev_languages = None
    plot_style: str = '_mpl-gallery'
    repo_dir: Path = Path(__file__).parents[1]
    data_dir: Path = repo_dir / 'data'
    output_dir: Path = repo_dir / 'output'
    base_layer_image: Path = data_dir / 'car-prefets.png'
    text_effect = define_path_effect(linewidth=1, foreground='white', alpha=0.9)


project_starts = {
    'linguistics': {
        '1991': {'sag'},
        '1993': {'axk', 'mzv'},
        '1994': {'ksp'},
        '1995': {'ndy'},
        '2001': {'mcx'},
        '2009': {'nzk'},
        '2017': {'gbv', 'ngd', 'yky'},
        '2018': {'aiy', 'bjo', 'mdn', 'nbm', 'ngg'},
        '2019': {'bdt', 'bff', 'kbn', 'mdd', 'pnz', 'sqm', 'yaj'},
        '2020': {'gbq', 'vae'},
        '2021': {'bfl', 'bkj', 'bqk', 'lna'},
        '2022': {'fuu', 'gbg', 'moj'},
    },
    'translation': {
        '1993': {'axk', 'gbp', 'gso', 'ksp', 'lnl', 'mcx', 'mzv'},
        '2003': {'nzk'},
        '2008': {'bdt', 'liy', 'ndy'},
        '2009': {'bdt'},
        '2023': {'aiy', 'bff', 'bjo', 'bkj', 'gbv', 'gso', 'kbn', 'mdn', 'ngd', 'vae', 'yaj'},
    },
    'literacy': {
        '1990': {'sag'},
    },
}

# Get sequential list of years.
yrs = [yr for k, v in project_starts.items() for yr in v.keys()]
yrs = list(set(yrs))
yrs.sort()

# Initialize data dict.
years = dict()
for i, year in enumerate(yrs):
    for data in project_starts.values():
        for yr, lgs in data.items():
            if yr == year:
                # Add current year's languages.
                if not years.get(yr):
                    years[yr] = lgs
                else:
                    years[yr].update(lgs)
                # Add previous year's languages.
                if i > 0:
                    years[yr].update(years.get(yrs[i-1]))
                break
