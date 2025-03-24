from . import __config__
from .layers import create_layer
from .layers import get_composite_image


def get_outfile_name(full_filename):
    if __config__.filename:
        full_filename = f"{__config__.filename}.png"
    return full_filename


def create_location_map():
    filename = get_outfile_name('car-language-locations-map.png')
    outfile = __config__.output_dir / filename
    images = []
    images.append(create_layer('base'))
    images.append(create_layer('locations'))
    img = get_composite_image(images)
    img.save(outfile)


def create_population_map():
    filename = get_outfile_name('car-language-populations-map.png')
    outfile = __config__.output_dir / filename
    images = []
    images.append(create_layer('base'))
    images.append(create_layer('populations'))
    img = get_composite_image(images)
    img.save(outfile)


def create_project_status_map():
    filename = get_outfile_name('car-language-project-status-map.png')
    outfile = __config__.output_dir / filename
    images = []
    images.append(create_layer('base'))
    images.append(create_layer('project_status'))
    img = get_composite_image(images)
    img.save(outfile)