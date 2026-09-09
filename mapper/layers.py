import matplotlib.pyplot as plt
import shutil
import sys

from highlight_text import ax_text
from PIL import Image

from . import __config__
from .data import get_cag_lgs_info_csv
from .svg import SvgImage


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
        sizes = [__config__.geometry.dot_radius_factor for v in values]
    elif category == 'population':
        sizes = [max(int((v/3.1416)**(0.5)*__config__.geometry.dot_basic_radius_factor), 1) for v in values]
    return sizes


def setup_plot():
    plt.style.use(__config__.plot_style)
    fig, ax = plt.subplots()
    fig.set_size_inches(__config__.geometry.img_w_in, __config__.geometry.img_h_in)  # @96dpi
    return fig, ax


def add_annotations(names, x, y, position='center', ax=None):
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

    if ax is not None:
        props = {
            "Ali": [(306, 357), "aiy"],
            "Banda-Linda": [(535, 286), "liy"],
            "Banda-Mbrès": [(503, 267), "bqk"],
            "Banda-Ndélé": [(523, 235), "bfl"],
            # "Banda-Yangere": [(513, 223), "yaj"],
            "Bhofi": [(235, 492), "bff"],
            "Bhogongo": [(97, 319), "bkj"],
            "Bhogoto": [(118, 436), "bdt"],
            "Fulu": [(369, 410), "fuu"],
            "Gbagiri": [(540, 314), "bdt"],
            "Gbanu": [(271, 331), "gbv"],
            "Gbanziri": [(429, 439), "gbg"],
            "Gbaya Bhianda": [(61, 377), "gso"],
            "Gbaya-Bozoum": [(52, 273), "gbq"],
            "Gbeya": [(314, 206), "gbp"],
            "Kab(b)a": [(208, 182), "ksp"],
            "Kaba Markunda": [(228, 158), "ksp"],
            "Kare": [(189, 203), "kbn"],
            # "Langba": [(555, 392), "lna"],
            "Langbashe": [(571, 405), "lna"],
            "Luto": [(394, 136), "ndy"],
            "Mandja": [(430, 160), "mzv"],
            "Mbati": [(323, 466), "mdn"],
            "Mbum": [(123, 242), "mdd"],
            "Monzombo": [(379, 488), "moj"],
            "Mpyemo": [(124, 464), "mcx"],
            "Ngando": [(283, 490), "ngd"],
            "Ngbaka-Manza": [(472, 138), "ngg"],
            "Ngbugu": [(507, 448), "lnl"],
            "Ngombe": [(109, 409), "nmj"],
            "Nzakara": [(570, 372), "nzk"],
            "Pana": [(155, 221), "pnz"],
            "Sango": [(364, 439), "sag"],
            "Suma": [(292, 184), "sqm"],
            "Tali": [(130, 299), "kbn"],
            "Vale": [(397, 180), "vae"],
            "Yaka": [(178, 488), "axk"],
            "Yakoma": [(573, 431), "yky"],
            "Yakpa": [(547, 341), "bjo"],
            "Yangere (Kra)": [(71, 348), "yaj"],
        }
        scale = 3 / 4
        yshift = 15
        for i, name in enumerate(names):
            map_name = None
            xt, yt = (200 * scale, 300 * scale)
            for k in props:
                if k in name:
                    map_name = k
                    xt, yt = (v * scale for v in props.get(k)[0])
                    yt += yshift
                    break
            if map_name is None:
                continue
            # print(f"{name} @({xt}, {yt})")
            ax.annotate(
                map_name,
                xy=(x[i], y[i]),
                xycoords="data",
                fontsize=12,
                alpha=1,
                color=__config__.colors.text,
                # rotation=__config__.geometry.text_rotation,
                # ha=ha,
                # va=va,
                xytext=(xt, 576 * scale - yt),
                # textcoords="offset fontsize",
                textcoords="axes points",
                arrowprops={
                    "arrowstyle": "-",
                    # "connectionstyle": "angle3",
                    "color": __config__.colors.text,
                    "shrinkA": 0.05,
                    # "headwidth": 0,
                    # "headlength": 0,
                },
                annotation_clip=False,
            )
    else:
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
    xlim = (__config__.geometry.lon_min, __config__.geometry.lon_max)
    ylim = (__config__.geometry.lat_min, __config__.geometry.lat_max)
    ax.set(xlim=xlim, ylim=ylim, xticks=(), yticks=())
    ax.set_aspect('equal', adjustable='box')

    # Hide spines.
    for spine in plt.gca().spines.values():
        spine.set_visible(False)

    # Save image file.
    plt.savefig(outfile, format=__config__.output_image_format, dpi=375, transparent=True)
    # plt.show()
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
    add_annotations(names, x, y, position='offset', ax=ax)

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
    outfile = (__config__.output_dir / f"layer_{layer_name}").with_suffix(f".{__config__.output_image_format}")
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
    # Assume layers are passed in order from bottom to top.
    img = None
    base = layers.pop(0)
    if __config__.output_image_format == "svg":
        # Define base "prefectures" layer.
        base_img = SvgImage(base, id="0", label=base.stem)
        # REF: svg/geoViewBox
        base_img.lat_min = 2.219468
        base_img.lat_max = 11.007742
        base_img.lon_min = 14.421468

        # Define the output image itself; add base layer.
        img = SvgImage()
        img.add_inkscape_layer(base_img)
        # Add script-generated layers.
        for i, layer in enumerate(layers):
            layer_img = SvgImage(layer, id=f"{i + 1}", label=layer.stem)
            img.add_inkscape_layer(layer_img)

    elif __config__.output_image_format == "png":
        with Image.open(base) as img:
            for layer in layers:
                with Image.open(layer) as i:
                    img.paste(i, __config__.geometry.offset_png_base_image, mask=i)

    return img
