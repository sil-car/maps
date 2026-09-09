import re

from lxml import etree

from . import __config__


class SvgImage:
    """Provide similar API to PIL's Image class for PNG files."""

    PT2PX = __config__.geometry.dpi / 72
    SVG_NS = "http://www.w3.org/2000/svg"
    INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
    XLINK_NS = "http://www.w3.org/1999/xlink"
    NSMAP = {None: SVG_NS, "inkscape": INKSCAPE_NS, "xlink": XLINK_NS}  # noqa

    def __init__(self, filepath=None, id=None, label=None):
        self.xml_tree = None
        if filepath is not None:
            self.xml_tree = etree.parse(filepath)
        else:
            # Initialize self.xml_tree for the image itself.
            # NOTE: Use px instead of pt for clarity's sake.
            height = __config__.geometry.dpi * __config__.geometry.img_h_in
            width = __config__.geometry.dpi * __config__.geometry.img_w_in
            self._init_xml_tree(width, height)

        self.id = None
        if id is not None:
            self.id = id

        self.label = None
        if label is not None:
            self.label = label

        # Set default values.
        self.lat_min = __config__.geometry.lat_min
        self.lat_max = __config__.geometry.lat_max
        self.lon_min = __config__.geometry.lon_min
        # print(f"{self.label}: {self.width=}; {self.height=}")
        # print(f"{self.label}: {self.lat_min=}; {self.lat_max=}; {self.lon_min=}")
        self.fill = __config__.colors.map_area
        self.stroke = __config__.colors.map_line

    @property
    def height(self) -> str:
        """Return the literal value of the <svg> `height` attribute."""
        if self.root is not None:
            return self.root.get("height")

    @property
    def height_px(self) -> float:
        """Return the value in px of the <svg> `height` attribute.
        Convert from pt if needed."""
        return self._ensure_px(self.height)

    @property
    def ppdeg(self):
        return self.height_px / (self.lat_max - self.lat_min)

    @property
    def root(self):
        if self.xml_tree is not None:
            return self.xml_tree.getroot()

    @property
    def width(self):
        if self.root is not None:
            return self.root.get("width")

    @property
    def width_px(self):
        return self._ensure_px(self.width)

    @property
    def xml(self):
        if self.xml_tree is not None:
            return etree.tostring(self.xml_tree, encoding="UTF-8", pretty_print=True, xml_declaration=True).decode()

    def add_inkscape_layer(self, svg_image):
        """Add SVG file's data as new Inkscape layer on top of existing layers."""

        # NOTE: If the layer's dims are in pt, then everything needs to be
        # scaled into px values to match the pre-defined image size.
        # print(f"{svg_image.label}: {svg_image.width=}; {svg_image.height=}")
        # print(f"{svg_image.label}: {svg_image.lat_min=}; {svg_image.lat_max=}; {svg_image.lon_min=}")

        # Update XML with prefixed IDs to avoid collisions.
        self.prefix_ids(svg_image.root, svg_image.id)

        # Add XML as new "g" child element to base XML.
        scale, (dx, dy) = self.get_transform(svg_image).values()
        attrib = {
            "id": svg_image.id,
            f"{{{self.INKSCAPE_NS}}}label": svg_image.label,
            f"{{{self.INKSCAPE_NS}}}groupmode": "layer",
            "transform": f"scale({scale}) translate({dx} {dy})",
            "fill": svg_image.fill,
            "stroke": svg_image.stroke,
        }
        g = etree.SubElement(
            self.root,
            "g",
            attrib=attrib,
        )
        for child in svg_image.root:
            g.append(child)

    def get_transform(self, svg_layer):
        # Scale is determined by:
        # - img units compared with layer units (i.e. same px/deg)
        # - img extents compared with layer extents (i.e. same lat/lon window size)
        scale = 1
        if svg_layer.height.endswith("pt"):
            scale *= __config__.geometry.dpi / 72
            # print(f"{svg_layer.label}: {scale=}")
        scale *= self.ppdeg / svg_layer.ppdeg
        # print(f"{svg_layer.label}: {scale=}; {self.ppdeg=}; {svg_layer.ppdeg=}")
        # Translate is determined by:
        # - differences between lat_maxes and lon_mins (i.e. same window location)
        # NOTE: It's not clear why the translation is multiplied by the layer's
        # ppdeg instead of the image's, but this produces the correct result.
        dx = (svg_layer.lon_min - self.lon_min) * svg_layer.ppdeg  # x=0 @ left
        dy = -1 * (svg_layer.lat_max - self.lat_max) * svg_layer.ppdeg  # y=0 @ top
        # print(f"{svg_layer.label}: {dx=}; {dy=}")
        if svg_layer.height.endswith("pt"):
            dx *= __config__.geometry.dpi / 72
            dy *= __config__.geometry.dpi / 72
            # print(f"{svg_layer.label}: {dx=}; {dy=}")
        return {"scale": scale, "translate": (dx, dy)}

    def save(self, outfile_path):
        etree.ElementTree(self.root).write(
            outfile_path, pretty_print=True, xml_declaration=True, encoding="UTF-8"
        )

    def prefix_ids(self, root, prefix):
        """Rewrite every id and every reference to it (url(#id), xlink:href, href) with a prefix."""
        id_map = {}
        for el in root.iter():
            old_id = el.get("id")
            if old_id:
                new_id = f"{prefix}_{old_id}"
                id_map[old_id] = new_id
                el.set("id", new_id)

        url_pattern = re.compile(r"url\(#([^)]+)\)")

        def rewrite(value):
            if value and value.startswith("#") and value[1:] in id_map:
                return "#" + id_map[value[1:]]
            if value and "url(#" in value:
                def repl(m):
                    old = m.group(1)
                    return f"url(#{id_map.get(old, old)})"
                return url_pattern.sub(repl, value)
            return value

        href_attrs = [
            f"{{{self.XLINK_NS}}}href", "href",
            "fill", "stroke", "clip-path", "mask", "filter",
        ]
        for el in root.iter():
            for attr in href_attrs:
                val = el.get(attr)
                new_val = rewrite(val)
                if new_val != val:
                    el.set(attr, new_val)

    def _init_xml_tree(self, width, height):
        root = etree.Element(
            "svg",
            nsmap=self.NSMAP,
            attrib={
                "width": str(width),
                "height": str(height),
                "viewBox": f"0 0 {width} {height}",
            },
        )
        self.xml_tree = etree.ElementTree(root)

    def _ensure_px(self, value):
        if value.endswith("pt"):
            value = float(value.removesuffix("pt")) * self.PT2PX
        else:
            value = float(value)
        return value
