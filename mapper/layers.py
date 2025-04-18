import matplotlib.pyplot as plt
import shutil
import sys
from highlight_text import ax_text
from PIL import Image
from . import __config__
from .data import get_cag_lgs_info_csv


def error_exit(message=None):
    if message:
        print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def create_base_layer(**kwargs):
    shutil.copy(__config__.base_layer_image, kwargs.get('outfile'))


def get_dot_colors(values, category='equal'):
    if category == 'equal':
        colors = [__config__.colors.dot_basic for v in values]
    elif category == 'previous':
        colors = [__config__.colors.dot_prev for v in values]
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


def add_annotations(names, x, y, position='center'):
    if not __config__.show_names:
        return

    if position == 'offset':
        ha = 'left'
        va = 'bottom'
        textalign = 'left'
    else:
        ha = 'center'
        va = 'center'
        textalign = 'center'

    for i, name in enumerate(names):
        ax_text(
            x=x[i],
            y=y[i],
            s=f"<{name}>",
            fontsize=8,
            color=__config__.colors.text,
            rotation=__config__.geometry.text_rotation,
            highlight_textprops=[
                {
                    'path_effects': __config__.text_effect,
                    'color': __config__.colors.text,
                },
            ],
            ha=ha,
            va=va,
            textalign=textalign,
        )


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
    add_annotations(names, x, y, position='offset')

    # Finish & save plot.
    finish_and_save_plot(ax, outfile)


def create_previous_population_layer(**kwargs):
    outfile = kwargs.get('outfile')

    # Retrieve data.
    if not __config__.prev_languages:
        error_exit('No previous languages to map.')
    x, y, names, populations, stages = get_cag_lgs_info_csv(__config__.prev_languages)

    # Set dot sizes.
    sizes = get_dot_sizes(populations, category='population')

    # Set dot colors.
    colors = get_dot_colors(names, category='previous')

    # Prepare plot.
    fig, ax = setup_plot()

    # Add data & labels (annotations).
    ax.scatter(
        x, y,
        s=sizes,
        facecolors=colors,
        alpha=__config__.geometry.dot_prev_alpha,
    )
    if __config__.show_names is not False:
        add_annotations(names, x, y, position='center')

    # Finish & save plot.
    finish_and_save_plot(ax, outfile)


def create_population_layer(**kwargs):
    outfile = kwargs.get('outfile')

    # Retrieve data.
    if __config__.prev_languages:
        langs = {lg for lg in __config__.languages if lg not in __config__.prev_languages}
    else:
        langs = __config__.languages
    x, y, names, populations, stages = get_cag_lgs_info_csv(langs)

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
    if __config__.show_names is not False:
        add_annotations(names, x, y, position='center')

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
    add_annotations(names, x, y, position='center')

    # Finish & save plot.
    finish_and_save_plot(ax, outfile)


def create_layer(layer_name):
    outfile = (__config__.output_dir / f"layer_{layer_name}").with_suffix('.png')
    funcs = {
        'base': (create_base_layer, {'outfile': outfile}),
        'locations': (create_location_layer, {'outfile': outfile}),
        'previous_populations': (create_previous_population_layer, {'outfile': outfile}),
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