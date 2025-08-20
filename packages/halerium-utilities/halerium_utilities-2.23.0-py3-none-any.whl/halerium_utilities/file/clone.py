import shutil

from .card_ids import (assign_new_card_ids_to_board_file,
                       assign_new_card_ids_to_tree)


def clone_board_file(src, dst):
    """Clone board file.

    Creates a copy of the board file with all card ids replaced by new ids.

    Parameters
    ----------
    src :
        The file path or descriptor of board file to clone.
    dst :
        The file path or descriptor of the cloned board.

    Returns
    -------

    """
    assign_new_card_ids_to_board_file(board_file=src, new_board_file=dst, new_id_for_old_id=dict())


def clone_tree(src, dst, symlinks=False, ignore=None, copy_function=shutil.copy2, ignore_dangling_symlinks=False):
    """Clone directory tree.

    Creates a copy of a directory tree and assigns new ids to all cards
    in all board files in the copy of the tree.
    Then replaces all old card ids with these new card ids
    in all notebook and text files in the copy of the tree.

    Note that the parent directory where the root of the cloned tree will
    be placed should already exist, but not the root of the cloned directory
    tree itself.

    Parameters
    ----------
    src :
        The root of the directory tree to clone.
    dst :
        The root of the cloned directory tree.
        Note that this directory itself should not exist yet (since it is
        the path of the cloned tree's root), but its parent directory should
        already exist.
    symlinks : bool, optional
        Whether to copy symbolic links as symbolic links.
        The default is `False`, in which case the content is copied.
    ignore : optional
        The files or patterns to ignore.
    copy_function :
        The copy function to use for copying files.
        The default is `shutil.copy2`.
    ignore_dangling_symlinks :
        Whether to ignore dangling symbolic links.
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
    if ignore is None:
        ignore = shutil.ignore_patterns("*.ipynb_checkpoints")
    elif isinstance(ignore, str):
        ignore = shutil.ignore_patterns(ignore)
    elif isinstance(ignore, (list, tuple)):
        ignore = shutil.ignore_patterns(*ignore)
    shutil.copytree(src, dst, symlinks=symlinks, ignore=ignore, copy_function=copy_function, ignore_dangling_symlinks=ignore_dangling_symlinks)
    board_filenames, notebook_filenames, text_filenames = assign_new_card_ids_to_tree(dst, include_symlinks=False)

    return board_filenames, notebook_filenames, text_filenames
