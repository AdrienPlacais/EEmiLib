"""Gather GUI style-related objects.

In particular, define functions to display math equations.

"""

import io
import logging
import re

import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

TITLE_STYLE = "QGroupBox { font-size: 14px; font-weight: bold; }"
FILE_LIST_MAX_HEIGHT = 40

#: DPI used when rasterising mathtext labels.
MATH_LABEL_DPI = 150
#: Font size (pt) passed to matplotlib.
MATH_LABEL_FONTSIZE = 6


def _parse_key(key: str) -> tuple[str, str]:
    """Split *key* into ``(text, units)``.

    Parameters
    ----------
    key :
        String following the ``"text with possible $math$ [units]"``
        convention. Any of the parts may be absent.

    Returns
    -------
    str
        Content before the first ``[...]``.
    str
        Content between the first ``[...]``, without the brackets.

    """
    units_match = re.search(r"\[([^\]]+)\]\s*$", key)
    if units_match:
        units = units_match.group(1).strip()
        body = key[: units_match.start()].strip()
    else:
        units = ""
        body = key.strip()
    return body, units


def _compose_mathtext(body: str, units: str) -> str:
    """Assemble *body* and *units* into a single matplotlib mathtext string.

    Parameters
    ----------
    body :
        Mixed plain/math string (may contain any number of ``$...$``
        environments).
    units :
        Unit string without brackets (may be empty).

    Returns
    -------
    str
        A string suitable for ``matplotlib`` mathtext rendering, where
        units are typeset upright inside a math environment.

    """
    parts: list[str] = []
    if body:
        parts.append(body)
    if units:
        parts.append(f"$\\,\\mathrm{{[{units}]}}$")
    return " ".join(parts)


def _math_text_label(
    body: str,
    units: str,
    fontsize: int = MATH_LABEL_FONTSIZE,
    dpi: int = MATH_LABEL_DPI,
) -> QLabel:
    """Render a mixed plain/math/unit string as a ``QLabel`` pixmap.

    Parameters
    ----------
    body:
        Mixed plain/math string (may contain any number of ``$...$``
        environments).
    units :
        Unit string without brackets (may be empty).
    fontsize :
        Font size in points passed to matplotlib.
    dpi :
        Resolution used when rasterising the figure.

    Returns
    -------
    QLabel
        Label whose pixmap contains the rendered text, with a transparent
        background.  Falls back to a plain ``QLabel(text)`` if rendering
        fails.

    """
    text = _compose_mathtext(body, units)

    label = QLabel()
    label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

    try:
        fig = plt.figure(figsize=(0.01, 0.01))
        t = fig.text(0, 0, text, fontsize=fontsize)

        buf = io.BytesIO()
        fig.savefig(
            buf,
            format="png",
            dpi=dpi,
            bbox_inches=t.get_window_extent(
                renderer=fig.canvas.get_renderer()
            ).transformed(fig.dpi_scale_trans.inverted()),
            transparent=True,
        )
        plt.close(fig)
        buf.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buf.read())
        label.setPixmap(pixmap)

    except Exception as exc:
        logging.warning(
            f"mathtext rendering failed for {text!r}, "
            f"falling back to plain text.\n{exc}"
        )
        plt.close("all")
        label.setText(text)

    return label


def math_text_label_from_key(
    key: str,
    fontsize: int = MATH_LABEL_FONTSIZE,
    dpi: int = MATH_LABEL_DPI,
) -> QLabel:
    """Convenience wrapper: parse *key* then render it.

    Parameters
    ----------
    key :
        String following the ``"prefix $math$ [units]"`` convention.
    fontsize :
        Font size in points passed to matplotlib.
    dpi :
        Resolution used when rasterising the figure.

    Returns
    -------
    QLabel
        Rendered label ready to be passed to ``QTableWidget.setCellWidget``.

    """
    body, units = _parse_key(key)
    return _math_text_label(body, units, fontsize=fontsize, dpi=dpi)
