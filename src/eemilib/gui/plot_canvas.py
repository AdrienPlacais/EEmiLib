"""Define a tabbed collection of embedded matplotlib canvases."""

from matplotlib.axes import Axes
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget


class PlotCanvas(QWidget):
    """A single matplotlib Figure embedded as a Qt widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Instantiate the canvas with a fresh, empty Figure."""
        super().__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)

    def new_axes(self) -> Axes:
        """Clear the figure and return a fresh Axes."""
        self.figure.clear()
        return self.figure.add_subplot(111)

    def refresh(self) -> None:
        """Redraw the canvas to reflect any changes made to its Axes."""
        self.canvas.draw_idle()


class TabbedPlotArea(QWidget):
    """A tab per impact energy, each holding its own :class:`PlotCanvas`.

    Also supports a single, unlabelled tab for the non-grouped case (plain
    ``Axes``, not keyed by impact energy).

    """

    #: Label used for the tab in the non-grouped (single-Axes) case.
    _SINGLE_TAB_LABEL = "Plot"

    def __init__(self, parent: QWidget | None = None) -> None:
        """Instantiate an empty tab widget."""
        super().__init__(parent)
        self._tabs = QTabWidget()
        self._canvases: dict[float, PlotCanvas] = {}

        layout = QVBoxLayout(self)
        layout.addWidget(self._tabs)
        layout.setContentsMargins(0, 0, 0, 0)

    def clear(self) -> None:
        """Remove every tab (called by ``"Clear figure"``)."""
        self._tabs.clear()
        self._canvases = {}

    def axes_for(self, e_pe: float | None) -> Axes:
        """Return the (creating if needed) Axes for the given impact energy.

        Parameters
        ----------
        e_pe :
            Impact energy this tab corresponds to, or ``None`` for the
            single, non-grouped case.

        Return
        ------
            A fresh or existing ``Axes`` to plot into.

        """
        key = -1.0 if e_pe is None else e_pe
        canvas = self._canvases.get(key)
        if canvas is None:
            canvas = PlotCanvas()
            label = self._SINGLE_TAB_LABEL if e_pe is None else f"{e_pe:g} eV"
            self._tabs.addTab(canvas, label)
            self._canvases[key] = canvas

        axes = canvas.figure.axes
        if axes:
            return axes[0]
        return canvas.new_axes()

    def refresh(self, e_pe: float | None = None) -> None:
        """Redraw one canvas (``e_pe`` given) or every canvas (otherwise)."""
        if e_pe is not None:
            key = e_pe
            canvas = self._canvases.get(key)
            if canvas is not None:
                canvas.refresh()
            return
        for canvas in self._canvases.values():
            canvas.refresh()

    def has_any_lines(self) -> bool:
        """Tell whether any tab currently holds plotted data."""
        return any(
            len(canvas.figure.axes) > 0
            and len(canvas.figure.axes[0].get_lines()) > 0
            for canvas in self._canvases.values()
        )
