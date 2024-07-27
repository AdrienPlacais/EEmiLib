"""Define the model related interface in the GUI."""

from eemilib.gui.helper import PARAMETER_ATTR_TO_POS
from PyQt5.QtWidgets import QGroupBox, QTableWidget, QVBoxLayout


def model_configuration() -> tuple[QGroupBox, QTableWidget]:
    """Set the interface related to the model specific parameters."""
    group = QGroupBox("Model configuration")
    layout = QVBoxLayout()

    model_table = QTableWidget(0, 7)
    model_table.setHorizontalHeaderLabels(list(PARAMETER_ATTR_TO_POS.keys()))
    model_table.setMaximumHeight(1000)
    model_table.setMinimumHeight(200)
    layout.addWidget(model_table)

    group.setLayout(layout)
    return group, model_table
    # main_layout.addWidget(group)
