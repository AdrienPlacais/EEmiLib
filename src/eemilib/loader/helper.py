"""Define some common helpers for loading data."""

from pathlib import Path

from eemilib.util.constants import col_energy


def read_header(
    filepath: str | Path,
    sep: str = "\t",
    comment: str = "#",
) -> tuple[list[str], int]:
    """Get the line describing columns content.

    It is the first line of the files that does not start with a comment
    character. Header of first column can be anything. Header of following
    columns must hold incidence angle and be convertable to a float.

    Parameters
    ----------
    filepath :
        Path to file holding data under study.
    sep :
        Column delimiter.
    comment :
        Comment character.

    Returns
    -------
    list[str]
        Columns descriptors. First column is ``Energy [eV]``. Following is/are
        ``theta [deg]``, where ``theta`` is the value of the incidence angle.
    int
        Number of comment lines before the header.

    """
    header = []
    n_comments = 0
    with open(filepath) as file:
        for n_comments, line in enumerate(file):
            if not line.startswith(comment):
                header = line.strip().split(sep)
                break
    if not header:
        raise OSError(
            f"Error reading {filepath}. It seems there is no uncommented line?"
            f"Comment character is {comment}."
        )

    return _format_header(header), n_comments


def _format_header(header: list[str]) -> list[str]:
    """Generate default header."""
    header[0] = col_energy
    header[1:] = [f"{float(h)} [deg]" for h in header[1:]]
    return header


def read_comments(filepath: str | Path, comment: str = "#") -> list[str]:
    """Read the comments in the file.

    Parameters
    ----------
    filepath :
        Path to file holding data under study.
    comment :
        Comment character.

    Returns
    -------
    list[str]
        Comments, line by line. Without the comment character.

    """
    comments: list[str] = []
    with open(filepath) as file:
        for line in file:
            if not line.startswith(comment):
                return comments
            comments.append(line[1:])
    return comments
