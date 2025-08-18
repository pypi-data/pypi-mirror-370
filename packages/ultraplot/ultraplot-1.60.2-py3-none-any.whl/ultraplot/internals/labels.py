#!/usr/bin/env python3
"""
Utilities related to matplotlib text labels.
"""
import matplotlib.patheffects as mpatheffects
import matplotlib.text as mtext

from . import ic  # noqa: F401


def _transfer_label(src, dest):
    """
    Transfer the input text object properties and content to the destination
    text object. Then clear the input object text.
    """
    text = src.get_text()
    dest.set_color(src.get_color())  # not a font property
    dest.set_fontproperties(src.get_fontproperties())  # size, weight, etc.
    if not text.strip():  # WARNING: must test strip() (see _align_axis_labels())
        return
    dest.set_text(text)
    src.set_text("")


def _update_label(text, props=None, **kwargs):
    """
    Add a monkey patch for ``Text.update`` with pseudo "border" and "bbox"
    properties without wrapping the entire class. This facillitates inset titles.
    """
    props = props or {}
    props = props.copy()  # shallow copy
    props.update(kwargs)

    # Update border
    border = props.pop("border", None)
    bordercolor = props.pop("bordercolor", "w")
    borderinvert = props.pop("borderinvert", False)
    borderwidth = props.pop("borderwidth", 2)
    borderstyle = props.pop("borderstyle", "miter")

    if border:
        facecolor, bgcolor = text.get_color(), bordercolor
        if borderinvert:
            facecolor, bgcolor = bgcolor, facecolor
        kw = {
            "linewidth": borderwidth,
            "foreground": bgcolor,
            "joinstyle": borderstyle,
        }
        text.set_color(facecolor)
        text.set_path_effects(
            [mpatheffects.Stroke(**kw), mpatheffects.Normal()],
        )
    # ISSUE: interfers with adding path effects when we border is False but we do apply path effects
    elif border is False and not text.get_path_effects():
        text.set_path_effects(None)
    # print(props.get("path_effects", []))

    # Update bounding box
    # NOTE: We use '_title_pad' and '_title_above' for both titles and a-b-c
    # labels because always want to keep them aligned.
    # NOTE: For some reason using pad / 10 results in perfect alignment for
    # med-large labels. Tried scaling to be font size relative but never works.
    pad = text.axes._title_pad / 10  # default pad
    bbox = props.pop("bbox", None)
    bboxcolor = props.pop("bboxcolor", "w")
    bboxstyle = props.pop("bboxstyle", "round")
    bboxalpha = props.pop("bboxalpha", 0.5)
    bboxpad = props.pop("bboxpad", None)
    bboxpad = pad if bboxpad is None else bboxpad
    if bbox is None:
        pass
    elif isinstance(bbox, dict):  # *native* matplotlib usage
        props["bbox"] = bbox
    elif not bbox:
        props["bbox"] = None  # disable the bbox
    else:
        props["bbox"] = {
            "edgecolor": "black",
            "facecolor": bboxcolor,
            "boxstyle": bboxstyle,
            "alpha": bboxalpha,
            "pad": bboxpad,
        }
    return mtext.Text.update(text, props)
