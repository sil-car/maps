from . import __config__
from .layers import create_layer
from .layers import get_composite_image


def create_location_map():
    outfile = __config__.output_dir / 'car-language-locations-map.png'
    images = []
    images.append(create_layer('base'))
    images.append(create_layer('locations'))
    img = get_composite_image(images)
    img.save(outfile)


def create_population_map():
    outfile = __config__.output_dir / 'car-language-populations-map.png'
    images = []
    images.append(create_layer('base'))
    images.append(create_layer('populations'))
    img = get_composite_image(images)
    img.save(outfile)


def create_project_status_map():
    outfile = __config__.output_dir / 'car-language-project-status-map.png'
    images = []
    images.append(create_layer('base'))
    images.append(create_layer('project_status'))
    img = get_composite_image(images)
    img.save(outfile)