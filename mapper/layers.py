import matplotlib.pyplot as plt
import shutil
from PIL import Image
from . import __config__
from .data import get_cag_lgs_info_csv


def create_base_layer(**kwargs):
    shutil.copy(__config__.base_layer_image, kwargs.get('outfile'))


def get_dot_colors(values, category='equal'):
    if category == 'equal':
        colors = [__config__.colors.dot_basic for v in values]
    elif category == 'status':
            # Add colors.
        color_map = {
            'done': 'green',
            'in progress': 'yellow',
            'near to publishing': 'yellow',
            'ongoing elsewhere (cameroon)': 'yellow',
            'pre-project': 'yellow',
            'unengaged': 'red',
        }
        colors = []
        for stage in values:
            c = color_map.get(stage.lower())
            if c:
                colors.append(c)
            else:
                colors.append(__config__.colors.dot)
    return colors


def get_dot_sizes(values, category='equal'):
    if category == 'equal':
        sizes = [1 for v in values]
    elif category == 'population':
        sizes = [max(int((v/3.1416)**(0.5)*__config__.geometry.dot_basic_radius_factor), 1) for v in values]
    return sizes


def setup_plot():
    plt.style.use(__config__.plot_style)
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 6) # @100dpi
    return fig, ax


def finish_and_save_plot(ax, outfile):
    # Adjust plot.
    ax.set(xlim=(14, 28), ylim=(2, 12), xticks=(), yticks=())
    ax.set_aspect('equal', adjustable='box')

    # Hide spines.
    for spine in plt.gca().spines.values():
        spine.set_visible(False)

    # Save image file.
    plt.savefig(outfile, format='png', dpi=375, transparent=True)
    plt.close()

def create_location_layer(**kwargs):
    outfile = kwargs.get('outfile')

    # Retrieve data.
    x, y, names, populations, stages = get_cag_lgs_info_csv()

    # Set dot sizes.
    sizes = get_dot_sizes(populations, category='equal')

    # Set dot colors.
    colors = get_dot_colors(names, category='equal')

    # Prepare plot.
    fig, ax = setup_plot()

    # Add data & labels (annotations).
    ax.scatter(x, y, s=sizes, facecolors=colors)
    for i, name in enumerate(names):
        ax.annotate(
            name,
            (x[i], y[i]),
            fontsize=8,
            color=__config__.colors.text,
            rotation=__config__.geometry.text_rotation,
            xytext=__config__.geometry.offset_location_text,
            textcoords='offset points',
            # horizontalalignment='center',
            # verticalalignment='center',
        )

    # Finish & save plot.
    finish_and_save_plot(ax, outfile)


def create_population_layer(**kwargs):
    outfile = kwargs.get('outfile')

    # Retrieve data.
    x, y, names, populations, stages = get_cag_lgs_info_csv()

    # Set dot sizes.
    sizes = get_dot_sizes(populations, category='population')

    # Set dot colors.
    colors = get_dot_colors(names, category='equal')

    # Prepare plot.
    fig, ax = setup_plot()

    # Add data & labels (annotations).
    ax.scatter(
        x, y,
        s=sizes,
        facecolors=colors,
        alpha=__config__.geometry.dot_basic_alpha,
    )
    for i, name in enumerate(names):
        ax.annotate(
            name,
            (x[i], y[i]),
            fontsize=8,
            color=__config__.colors.text,
            rotation=__config__.geometry.text_rotation,
            horizontalalignment='center',
            verticalalignment='center',
        )

    # Finish & save plot.
    finish_and_save_plot(ax, outfile)


def create_status_layer(**kwargs):
    outfile = kwargs.get('outfile')

    # Retrieve data.
    x, y, names, populations, stages = get_cag_lgs_info_csv()

    # Set dot sizes.
    sizes = get_dot_sizes(populations, category='population')

    # Set dot colors.
    colors = get_dot_colors(stages, category='status')

    # Prepare plot.
    fig, ax = setup_plot()

    # Add data & labels (annotations).
    ax.scatter(
        x, y,
        s=sizes,
        facecolors=colors,
        alpha=__config__.geometry.dot_basic_alpha,
    )
    for i, name in enumerate(names):
        ax.annotate(
            name,
            (x[i], y[i]),
            fontsize=8,
            color=__config__.colors.text,
            rotation=__config__.geometry.text_rotation,
            horizontalalignment='center',
            verticalalignment='center',
        )

    # Finish & save plot.
    finish_and_save_plot(ax, outfile)


def create_layer(layer_name):
    outfile = (__config__.output_dir / f"layer_{layer_name}").with_suffix('.png')
    funcs = {
        'base': (create_base_layer, {'outfile': outfile}),
        'locations': (create_location_layer, {'outfile': outfile}),
        'populations': (create_population_layer, {'outfile': outfile}),
        'project_status': (create_status_layer, {'outfile': outfile}),
    }

    [func, kwargs] = funcs.get(layer_name)
    func(**kwargs)
    return outfile


def get_composite_image(layers):
    """Assume layers are passed in order from bottom to top."""
    base = layers.pop(0)
    with Image.open(base) as img0:
        for layer in layers:
            with Image.open(layer) as img:
                img0.paste(img, __config__.geometry.offset_base_image, mask=img)
        
        return img0