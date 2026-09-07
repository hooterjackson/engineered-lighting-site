"""Lossless preprocessing of the KiCad SVG plots published with Doc 9.

Every transform here is text-level and topology-preserving:

  * XML prolog, DOCTYPE, <title> and the root <desc> are dropped
  * fill:#rrggbb / stroke:#rrggbb become currentColor (layer plots only) so the
    page's CSS tokens colour each layer -- the exported hex values are KiCad's
    editor colours, not the board's
  * invisible <text opacity="0"> nodes are removed (their stroked glyph paths
    are what actually draws)
  * <g class="stroked-text"><desc>REF</desc> gains data-ref="REF" and loses the
    <desc>, so the viewer can find a reference label without ids
  * solder-mask plots carry fill-opacity:0.4000 baked in; it is normalised to 1
    and the page controls opacity from CSS

No path data is rounded, merged, reordered or reformatted. verify() re-parses
the input and the output and fails on any change to the element census or to
any 'd' attribute.
"""

import re
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"

RE_PROLOG = re.compile(r"^\s*<\?xml[^>]*\?>\s*", re.S)
RE_DOCTYPE = re.compile(r"\s*<!DOCTYPE[^>]*>\s*", re.S)
RE_TITLE = re.compile(r"\s*<title>.*?</title>\s*", re.S)
RE_ROOT_TAG = re.compile(r"<svg\b.*?>", re.S)
RE_VIEWBOX = re.compile(r'viewBox="([^"]+)"')
RE_WIDTH = re.compile(r'width="([^"]+)"')
RE_HEIGHT = re.compile(r'height="([^"]+)"')
RE_COLOUR = re.compile(r"\b(fill|stroke):#[0-9A-Fa-f]{6}")
# A CAM rendering colours each element with an attribute, not a style.
RE_COLOUR_ATTR = re.compile(r'\b(fill|stroke)="#[0-9A-Fa-f]{6}"')
RE_BG_STYLE = re.compile(r'\s*style="background-color:[^"]*"')
RE_TEXT = re.compile(r"\s*<text\b[^>]*\bopacity=\"0\"[^>]*>.*?</text>", re.S)
RE_ANY_TEXT = re.compile(r"<text\b", re.S)
RE_STROKED = re.compile(r"<g class=\"stroked-text\">\s*<desc>([^<]*)</desc>")
RE_EMPTY_IDENTITY = re.compile(
    r"\s*<g style=\"[^\"]*\"\s*transform=\"translate\(0 0\) scale\(1 1\)\">\s*</g>", re.S
)
RE_MASK_OPACITY = re.compile(r"fill-opacity:0\.4000")
RE_HEX = re.compile(r"#[0-9A-Fa-f]{6}")


def _root_attrs(source):
    """viewBox / width / height of the original root element."""
    tag = RE_ROOT_TAG.search(source)
    if not tag:
        raise ValueError("no <svg> root element")
    tag = tag.group(0)
    vb = RE_VIEWBOX.search(tag)
    if not vb:
        raise ValueError("root <svg> has no viewBox")
    w = RE_WIDTH.search(tag)
    h = RE_HEIGHT.search(tag)
    return vb.group(1), (w.group(1) if w else None), (h.group(1) if h else None)


def _body(source):
    """Everything between the root <svg ...> tag and the final </svg>."""
    tag = RE_ROOT_TAG.search(source)
    end = source.rindex("</svg>")
    return source[tag.end():end]


def prepare(source, refs=(), recolour=True, normalise_mask=False, extra_attrs=None,
            wrap_transform=None, view_box=None):
    """Return (svg_text, stats). `refs` is the set of references whose stroked
    text labels should be tagged with data-ref on this sheet or layer.

    `wrap_transform` puts the whole body inside one extra group, which is how
    a CAM rendering is moved into the native-millimetre frame the rest of a
    viewer works in. `view_box` overrides the declared frame to match."""
    refs = set(refs)
    view_box_declared, width, height = _root_attrs(source)

    text = RE_BG_STYLE.sub("", source)
    text = RE_PROLOG.sub("", text)
    text = RE_DOCTYPE.sub("", text)
    text = RE_TITLE.sub("", text)

    body = _body(text)
    body = re.sub(r"\s*<desc>[^<]*</desc>", "", body, count=1)

    tagged = {"count": 0, "refs": set()}

    def _stroked(match):
        label = match.group(1)
        if label in refs:
            tagged["count"] += 1
            tagged["refs"].add(label)
            return '<g class="stroked-text" data-ref="%s">' % label
        return '<g class="stroked-text">'

    body = RE_STROKED.sub(_stroked, body)
    body = RE_TEXT.sub("", body)
    body = RE_EMPTY_IDENTITY.sub("", body)
    if recolour:
        body = RE_COLOUR.sub(r"\1:currentColor", body)
        body = RE_COLOUR_ATTR.sub(r'\1="currentColor"', body)
    if normalise_mask:
        body = RE_MASK_OPACITY.sub("fill-opacity:1.0000", body)

    if wrap_transform:
        body = '<g transform="%s">%s</g>' % (wrap_transform, body)
    if view_box:
        view_box_out = view_box
        width = height = None
    else:
        view_box_out = view_box_declared

    attrs = ['xmlns="%s"' % SVG_NS]
    if width:
        attrs.append('width="%s"' % width)
    if height:
        attrs.append('height="%s"' % height)
    attrs.append('viewBox="%s"' % view_box_out)
    for key, value in (extra_attrs or {}).items():
        attrs.append('%s="%s"' % (key, value))

    out = "<svg %s>%s</svg>\n" % (" ".join(attrs), body)
    stats = {
        "view_box": view_box_out,
        "data_ref_tags": tagged["count"],
        "data_ref_unique": len(tagged["refs"]),
        "tagged_refs": sorted(tagged["refs"]),
        "hex_colors_after": len(RE_HEX.findall(out)) if recolour else None,
        "text_after": len(RE_ANY_TEXT.findall(out)),
    }
    return out, stats


def census(svg_text):
    """{localname: count} plus the ordered list of every 'd' attribute."""
    root = ET.fromstring(svg_text)
    tags = {}
    paths = []
    for node in root.iter():
        name = node.tag.split("}")[-1]
        tags[name] = tags.get(name, 0) + 1
        if "d" in node.attrib:
            paths.append(node.attrib["d"])
    return tags, paths


def verify(source, result, added_groups=0):
    """Raise unless `result` has the same geometry as `source`.

    Only <text>, <desc>, <title> and one empty identity <g> may disappear.
    Every path 'd' string must survive token-identically and in order.
    """
    src_tags, src_paths = census(source)
    out_tags, out_paths = census(result)

    if src_paths != out_paths:
        for i, (a, b) in enumerate(zip(src_paths, out_paths)):
            if a != b:
                raise AssertionError("path %d changed:\n  %r\n  %r" % (i, a[:120], b[:120]))
        raise AssertionError(
            "path count changed: %d -> %d" % (len(src_paths), len(out_paths))
        )

    droppable = {"text", "desc", "title", "svg", "g"}
    for name, count in src_tags.items():
        after = out_tags.get(name, 0)
        if name in droppable:
            if after > count + (added_groups if name == "g" else 0):
                raise AssertionError("%s count grew: %d -> %d" % (name, count, after))
            continue
        if after != count:
            raise AssertionError("%s count changed: %d -> %d" % (name, count, after))
    for name, count in out_tags.items():
        if name not in src_tags:
            raise AssertionError("new element type %s appeared" % name)

    dropped_groups = src_tags.get("g", 0) + added_groups - out_tags.get("g", 0)
    if dropped_groups not in (0, 1):
        raise AssertionError("unexpected number of dropped groups: %d" % dropped_groups)
    if out_tags.get("text", 0):
        raise AssertionError("invisible text survived")
    if out_tags.get("desc", 0):
        raise AssertionError("desc survived")
    return {
        "paths": len(out_paths),
        "groups_before": src_tags.get("g", 0),
        "groups_after": out_tags.get("g", 0),
        "circles": out_tags.get("circle", 0),
        "text_before": src_tags.get("text", 0),
    }
