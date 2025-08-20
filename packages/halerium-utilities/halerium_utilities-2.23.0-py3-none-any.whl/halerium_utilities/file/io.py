import json
import os


from halerium_utilities.board import Board
from halerium_utilities.notebook.convert import (
    convert_to_native_format, convert_to_jupyter_format)
from halerium_utilities.migration.board import migrate_newest


_board_filename_endings = ".board"
_notebook_filename_endings = ".ipynb"
_text_filename_endings = (".py",)


def read_board(file, encoding="utf-8"):
    """Read board from file and migrate to newest version.

    Parameters
    ----------
    file :
        The file path or descriptor for the file to read the board from.
    encoding : optional
        The encoding the board file. Default is 'utf-8'
    Returns
    -------
    board :
        The board as read from file as a json-compatible structure.

    """
    with open(file, "r", encoding=encoding) as f:
        board = json.load(f)
    board = migrate_newest(board)[1]

    return Board(board)


def write_board(board: Board, file, encoding="utf-8"):
    """Write board to file.

    Parameters
    ----------
    board :
        The board to write.
    file :
        The file path or descriptor to write the board to.
    encoding : optional
        The encoding the board file. Default is 'utf-8'

    Returns
    -------

    """
    with open(file, "w", encoding=encoding) as f:
        json.dump(board.to_dict(), f, indent=0)


def read_notebook(file, encoding="utf-8", code_format="native"):
    """Read notebook from file.

    Parameters
    ----------
    file :
        The file path or descriptor to read the notebook from.
    encoding : optional
        The encoding the notebook file. Default is 'utf-8'
    code_format : optional
        The target format of the notebook cell source code.
        Can be either "native" for multiline string or
        "jupyter" for string arrays.

    Returns
    -------
    notebook:
        The notebook as read from file as a json-compatible structure.

    """
    with open(file, "r", encoding=encoding) as f:
        notebook = json.load(f)

    if code_format == "native":
        notebook = convert_to_native_format(notebook, inplace=True)
    elif code_format == "jupyter":
        notebook = convert_to_jupyter_format(notebook, inplace=True)
    else:
        raise ValueError("source_format must be either 'native' or 'jupyter'.")

    return notebook


def write_notebook(notebook, file, encoding="utf-8", code_format="native"):
    """Write notebook to file.

    Parameters
    ----------
    notebook :
        The notebook to write.
    file :
        The file path or descriptor to write the notebook to.
    encoding : optional
        The encoding the notebook file. Default is 'utf-8'
    code_format : optional
        The target format of the notebook cell source code.
        Can be either "native" for multiline string or
        "jupyter" for string arrays.

    Returns
    -------

    """
    if code_format == "native":
        notebook = convert_to_native_format(notebook, inplace=False)
        indent = None
    elif code_format == "jupyter":
        notebook = convert_to_jupyter_format(notebook, inplace=False)
        indent = 2
    else:
        raise ValueError("source_format must be either 'native' or 'jupyter'.")

    with open(file, "w", encoding=encoding) as f:
        json.dump(notebook, f, indent=indent)


def read_text_file(file, encoding="utf-8"):
    """Read text file.

    Parameters
    ----------
    file :
        The file path or descriptor to read the text from.
    encoding : optional
        The encoding the text file. Default is 'utf-8'

    Returns
    -------
    lines :
        The text from the file as a list of lines.

    """
    with open(file, "r", encoding=encoding) as f:
        lines = f.readlines()
    return lines


def write_text_file(lines, file, encoding="utf-8"):
    """Write text file.

    Parameters
    ----------
    lines:
        The text to write as a list of lines.
    file :
        The file path or descriptor to write to.
    encoding : optional
        The encoding the text file. Default is 'utf-8'

    Returns
    -------

    """
    with open(file, "w", encoding=encoding) as f:
        f.writelines(lines)


def get_board_notebook_and_text_filenames_in(filenames):
    """Get board, notebook, and text file names in list of files.

    Parameters
    ----------
    filenames :
        The list of file names.

    Returns
    -------
    board_filenames :
        The list of board file names in filenames.
    notebook_filenames :
        The list of notebook file names filenames.
    text_filenames :
        The list of text file names in filenames.

    """
    board_filenames = [f for f in filenames if f.endswith(_board_filename_endings)]
    notebook_filenames = [f for f in filenames if f.endswith(_notebook_filename_endings)]
    text_filenames = [f for f in filenames if f.endswith(_text_filename_endings)]

    return board_filenames, notebook_filenames, text_filenames


def get_board_notebook_and_text_filenames_in_tree(path, include_symlinks=False):
    """Get board, notebook, and text file names in directory tree.

    Return lists of all board, notebook, and text file names in a directory and
    all its subdirectories.

    Note that cycles in the directory structure can lead to infinite recursion,
    e.g. if symbolic links are included and such a link points to a parent
    directory of itself.

    Parameters
    ----------
    path :
        The path of the root of the directory tree.
    include_symlinks :
        Whether to include symbolic links.
        The default is `False`.

    Returns
    -------
    board_filenames :
        The list of board file names in tree.
    notebook_filenames :
        The list of notebook file names  in tree.
    text_filenames :
        The list of text file names in tree.

    """
    board_filenames = list()
    notebook_filenames = list()
    text_filenames = list()

    for root_dir, _, filenames in os.walk(path, followlinks=include_symlinks):

        for filename in filenames:
            filename = os.path.join(root_dir, filename)
            if (not include_symlinks) and os.path.islink(filename):
                continue    # pragma: no cover

            if filename.endswith(_board_filename_endings):
                board_filenames.append(filename)
            elif filename.endswith(_notebook_filename_endings):
                notebook_filenames.append(filename)
            elif filename.endswith(_text_filename_endings):
                text_filenames.append(filename)

    return board_filenames, notebook_filenames, text_filenames
