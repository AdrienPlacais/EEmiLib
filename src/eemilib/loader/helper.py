"""Define some common helpers for loading data."""

from importlib.resources.abc import Traversable
from pathlib import Path

from eemilib.util.constants import col_energy

#: .. todo::
#:    All loaders should support Traversable also
DataPath = str | Path | Traversable


def read_header(
    filepath: DataPath, sep: str = "\t", comment: str = "#"
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
    file = read_text(filepath)
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


def read_comments(filepath: DataPath, comment: str = "#") -> list[str]:
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
    file = read_text(filepath)
    for line in file:
        if not line.startswith(comment):
            return comments
        comments.append(line[1:])
    return comments


def read_text(filepath: DataPath) -> list[str]:
    """Read file contents regardless of path type or encoding.

    Accepts a plain string path, a :class:`~pathlib.Path`, or a
    :class:`~importlib.resources.abc.Traversable` (as returned by
    ``importlib.resources.files``). Falls back to Latin-1 if the file is not
    valid UTF-8, since some exported files (e.g. from CST) are Windows-encoded
    rather than UTF-8.

    """
    target = Path(filepath) if isinstance(filepath, str) else filepath
    try:
        return target.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return target.read_text(encoding="latin-1").splitlines()
