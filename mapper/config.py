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
    dot_basic_alpha: float = 0.7
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
    languages = 'all'
    plot_style: str = '_mpl-gallery'
    repo_dir: Path = Path(__file__).parents[1]
    data_dir: Path = repo_dir / 'data'
    output_dir: Path = repo_dir / 'output'
    base_layer_image: Path = output_dir / 'car-prefets.png'
    text_effect = define_path_effect(linewidth=1, foreground='white', alpha=0.9)
