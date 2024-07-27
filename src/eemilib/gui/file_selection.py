"""Define the file selection matrix."""

from collections.abc import Callable

from eemilib.util.constants import IMPLEMENTED_EMISSION_DATA, IMPLEMENTED_POP
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


def file_selection_matrix(
    main_window: QMainWindow,
) -> tuple[QGroupBox, list[list[None | QListWidget]]]:
    """Create the 4 * 3 matrix to select the files to load."""
    file_matrix_group = QGroupBox("Files selection matrix")
    file_matrix_layout = QGridLayout()

    row_labels, col_labels = IMPLEMENTED_POP, IMPLEMENTED_EMISSION_DATA
    n_rows, n_cols = len(row_labels), len(col_labels)

    file_lists: list[list[None | QListWidget]]
    file_lists = [[None for _ in range(n_cols)] for _ in range(n_rows)]

    for i, label in enumerate(row_labels):
        file_matrix_layout.addWidget(QLabel(label), i + 1, 0)

    for j, label in enumerate(col_labels):
        file_matrix_layout.addWidget(QLabel(label), 0, j + 1)

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

            file_matrix_layout.addLayout(cell_layout, i + 1, j + 1)

    file_matrix_group.setLayout(file_matrix_layout)
    return file_matrix_group, file_lists


def _setup_file_selection_widget(
    select_file_func: Callable,
) -> tuple[QPushButton, QListWidget]:
    """Set the button to load and the list of selected files."""
    button = QPushButton("📂")
    button.setFont(QFont("Segoe UI Emoji", 10))
    button.clicked.connect(select_file_func)

    file_list = QListWidget()
    return button, file_list


def _select_files(
    main_window: QMainWindow,
    files_list: list[list[None | QListWidget]],
    row: int,
    col: int,
) -> None:
    """Set up a function to set the filepaths."""
    options = QFileDialog.Options()
    file_names, _ = QFileDialog.getOpenFileNames(
        main_window,
        "Select Files",
        "",
        "All Files (*);;CSV Files (*.csv)",
        options=options,
    )
    if file_names:
        current_file_lists = files_list[row][col]
        assert current_file_lists is not None
        current_file_lists.clear()
        current_file_lists.addItems(file_names)
        # self.data_matrix.set_files(file_names, row=row, col=col)
