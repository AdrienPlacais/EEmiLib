"""Define the file selection matrix."""

from collections.abc import Callable

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
)

from eemilib.emission_data._data_matrix import DataMatrix
from eemilib.gui.helper import titled_group
from eemilib.gui.styles import FILE_LIST_MAX_HEIGHT
from eemilib.util.constants import IMPLEMENTED_EMISSION_DATA, IMPLEMENTED_POP


def file_selection_matrix(
    main_window: QMainWindow,
) -> tuple[QGroupBox, list[list[None | QListWidget]]]:
    """Create the 4 * 3 matrix to select the files to load."""
    layout = QGridLayout()
    group = titled_group("Files selection", layout)

    row_labels, col_labels = IMPLEMENTED_POP, IMPLEMENTED_EMISSION_DATA
    n_rows, n_cols = len(row_labels), len(col_labels)

    file_lists: list[list[None | QListWidget]]
    file_lists = [[None for _ in range(n_cols)] for _ in range(n_rows)]

    for i, label in enumerate(row_labels):
        layout.addWidget(QLabel(label), i + 1, 0)

    for j, label in enumerate(col_labels):
        layout.addWidget(QLabel(label), 0, j + 1)

    for i in range(n_rows):
        for j in range(n_cols):
            cell_layout = QHBoxLayout()
            button, file_list = _setup_file_selection_widget(
                lambda _, x=i, y=j: _select_files(
                    main_window, file_lists, x, y
                )
            )
            cell_layout.addWidget(button)
            cell_layout.addWidget(file_list)
            file_lists[i][j] = file_list

            layout.addLayout(cell_layout, i + 1, j + 1)

    group.setLayout(layout)
    return group, file_lists


def _setup_file_selection_widget(
    select_file_func: Callable, max_height: int | None = FILE_LIST_MAX_HEIGHT
) -> tuple[QPushButton, QListWidget]:
    """Set the button to load and the list of selected files."""
    button = QPushButton("📂")
    button.setFont(QFont("Segoe UI Emoji", 10))
    button.clicked.connect(select_file_func)

    file_list = QListWidget()
    if max_height is not None:
        file_list.setMaximumHeight(max_height)
    return button, file_list


def _select_files(
    main_window: QMainWindow,
    files_list: list[list[None | QListWidget]],
    row: int,
    col: int,
) -> None:
    """Set up a function to set the filepaths."""
    options = QFileDialog.Options()
    data_type = IMPLEMENTED_EMISSION_DATA[col]
    population = IMPLEMENTED_POP[row]
    file_names, _ = QFileDialog.getOpenFileNames(
        main_window,
        f"Select file(s) for {data_type} of {population}",
        "",
        "All Files (*);;CSV Files (*.csv)",
        options=options,
    )
    if file_names:
        current_file_lists = files_list[row][col]
        assert current_file_lists is not None
        current_file_lists.clear()
        current_file_lists.addItems(file_names)


def clear_filepaths_button(
    data_matrix: DataMatrix, files_list: list[list[None | QListWidget]]
) -> QPushButton:
    """Create a button to clear filepaths in data matrix and GUI."""
    clear_button = QPushButton(text="🧹 Clear files matrix")

    def _clear_filepaths() -> None:
        data_matrix.clear_filepaths()
        for line in files_list:
            for f in line:
                if f is None:
                    continue
                f.clear()

    clear_button.clicked.connect(_clear_filepaths)
    return clear_button


def clear_data_button(data_matrix: DataMatrix) -> QPushButton:
    """Create a button to clear loaded data."""
    clear_button = QPushButton(text="🗑️ Clear loaded data")

    def _clear_data() -> None:
        data_matrix.clear_data()

    clear_button.clicked.connect(_clear_data)
    return clear_button
