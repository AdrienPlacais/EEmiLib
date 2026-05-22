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
#: Fallback width (px) used for the first render, before the widget has
#: been laid out and its real width is known.
MATH_LABEL_DEFAULT_WIDTH_PX = 300


def _normalize_key(key: str) -> str:
    """Convert all RST ``:math:`...``` spans to ``$...$``.

    This allows keys written in either notation to go through the same
    rendering pipeline.

    Parameters
    ----------
    key :
        Raw key string, possibly containing ``:math:`...``` spans.

    Returns
    -------
    str
        Key with every ``:math:`...``` replaced by the equivalent ``$...$``.

    """
    return re.sub(r":math:`([^`]+)`", r"$\1$", key)


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
    key = _normalize_key(key)
    units_match = re.search(r"\[([^\]]+)\]\s*$", key)
    if units_match:
        units = units_match.group(1).strip()
        body = key[: units_match.start()].strip()
    else:
        units = ""
        body = key.strip()
    return body, units


def _render_to_pixmap(
    text: str,
    width_px: int,
    fontsize: int = MATH_LABEL_FONTSIZE,
    dpi: int = MATH_LABEL_DPI,
) -> QPixmap | None:
    """Render *text* as a matplotlib mathtext pixmap of *width_px* pixels.

    Parameters
    ----------
    text:
        Fully composed mathtext string (output of :func:`compose_mathtext`).
    width_px:
        Available horizontal space in pixels.  The figure is sized to this
        width so that matplotlib's ``wrap=True`` breaks lines at the correct
        point.
    fontsize:
        Font size in points.
    dpi:
        Rasterisation resolution.

    Returns
    -------
    QPixmap or None
        Rendered pixmap, or ``None`` if rendering failed.

    """
    if not text or width_px <= 0:
        return None

    width_in = max(width_px / dpi, 0.1)

    try:
        # Set figure width to the available column width so wrap=True
        # breaks lines at exactly the right point.
        fig = plt.figure(figsize=(width_in, 0.01))
        t = fig.text(
            0,
            0,
            text,
            fontsize=fontsize,
            wrap=True,
            horizontalalignment="left",
            verticalalignment="bottom",
        )

        renderer = fig.canvas.get_renderer()
        bbox = t.get_window_extent(renderer=renderer).transformed(
            fig.dpi_scale_trans.inverted()
        )

        # Clamp to a minimum size to avoid "tile cannot extend outside image".
        min_inches = 0.1
        bbox = bbox.expanded(
            max(min_inches / max(bbox.width, 1e-6), 1.0),
            max(min_inches / max(bbox.height, 1e-6), 1.0),
        )

        buf = io.BytesIO()
        fig.savefig(
            buf, format="png", dpi=dpi, bbox_inches=bbox, transparent=True
        )
        plt.close(fig)
        buf.seek(0)

        pixmap = QPixmap()
        pixmap.loadFromData(buf.read())
        return pixmap

    except Exception as exc:
        logging.warning(f"mathtext rendering failed for {text!r}.\n{exc}")
        plt.close("all")
        return None


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


class MathTextLabel(QLabel):
    """A ``QLabel`` that renders mixed plain/math text as a pixmap.

    Re-renders automatically whenever the widget is resized, so the text
    always wraps to fit the available column width.

    Parameters
    ----------
    body:
        Mixed plain/math string (may contain any number of ``$…$``
        environments).
    units:
        Unit string without brackets (may be empty).
    fontsize:
        Font size in points passed to matplotlib.
    dpi:
        Rasterisation resolution.

    """

    def __init__(
        self,
        body: str,
        units: str,
        fontsize: int = MATH_LABEL_FONTSIZE,
        dpi: int = MATH_LABEL_DPI,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._body = body
        self._units = units
        self._fontsize = fontsize
        self._dpi = dpi
        self._text = _compose_mathtext(body, units)
        self._last_width: int = 0

        self.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        # Do an initial render at a sensible default width so the label is
        # not blank before the first layout pass.
        self._render(MATH_LABEL_DEFAULT_WIDTH_PX)

    def resizeEvent(self, event) -> None:  # noqa: N802
        """Re-render the pixmap whenever the widget width changes."""
        super().resizeEvent(event)
        new_width = event.size().width()
        if new_width != self._last_width:
            self._last_width = new_width
            self._render(new_width)

    def _render(self, width_px: int) -> None:
        """Render at *width_px* and update the displayed pixmap."""
        pixmap = _render_to_pixmap(
            self._text, width_px, self._fontsize, self._dpi
        )
        if pixmap is not None:
            self.setPixmap(pixmap)
        else:
            # Fallback: plain text is always readable.
            self.setText(self._text)


def math_text_label_from_key(
    key: str,
    fontsize: int = MATH_LABEL_FONTSIZE,
    dpi: int = MATH_LABEL_DPI,
) -> tuple[QLabel, QLabel]:
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
    QLabel
        Rendered unit ready to be passed to ``QTableWidget.setCellWidget``.

    """
    body, units = _parse_key(key)
    label_body = MathTextLabel(body, "", fontsize=fontsize, dpi=dpi)
    label_unit = MathTextLabel("", units, fontsize=fontsize, dpi=dpi)
    return label_body, label_unit


def format_number(value: float) -> str:
    """Format the given number.

    Parameters
    ----------
    value :
        Number to format.

    """
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)
