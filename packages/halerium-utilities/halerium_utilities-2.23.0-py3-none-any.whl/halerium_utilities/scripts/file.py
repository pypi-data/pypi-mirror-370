import argparse

from ..file.card_ids import assign_new_card_ids_to_files as assign_new_card_ids_to_files_
from ..file.card_ids import assign_new_card_ids_to_tree as assign_new_card_ids_to_tree_
from ..file.clone import clone_board_file as clone_board_file_
from ..file.clone import clone_tree as clone_tree_
from ..file.io import get_board_notebook_and_text_filenames_in


def assign_new_card_ids_to_files(args=None):
    """Assign new card ids to files.

    Assign new ids to all cards in all boards in board files.
    Then replace all old card ids with these new card ids
    in the notebook and text files provided.
    The ids are replaced in-place.

    This is the console script version taking its parameters either
    from a string provided as `args`, or from the command line:

    usage: assign_new_card_ids_to_files [-h] [files [files ...]]

    positional arguments:
        files       The file(s) to assign new card ids to.

    optional arguments:
        -h, --help  show this help message and exit

    Parameters
    ----------
    args : str, None, optional
        The string containing the arguments.

    Returns
    -------

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('files', action="store", nargs='*', help='The file(s) to assign new card ids to.')
    args = parser.parse_args(args)

    board_files, notebook_files, text_files = get_board_notebook_and_text_filenames_in(args.files)
    assign_new_card_ids_to_files_(board_files, notebook_files, text_files)


def assign_new_card_ids_to_tree(args=None):
    """Assign new card ids to all files in directory tree.

    Assign new ids to all cards in all board files in a directory tree.
    Then replace all old card ids with these new card ids
    in all notebook and text files in the tree.
    The ids are replaced in-place.

    This is the console script version taking its parameters either
    from a string provided as `args`, or from the command line:

    usage: assign_new_card_ids_to_tree [-h] [--include_symlinks] path

    positional arguments:
      path                The root of the directory tree in which to assign new
                          card ids.

    optional arguments:
      -h, --help          show this help message and exit
      --include_symlinks  Include symbolic links.

    Parameters
    ----------
    args : str, None, optional
        The string containing the arguments.

    Returns
    -------

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='The root of the directory tree in which to assign new card ids.')
    parser.add_argument('--include_symlinks', action='store_true', default=False, help='Include symbolic links.')
    args = parser.parse_args(args)

    assign_new_card_ids_to_tree_(path=args.path, include_symlinks=args.include_symlinks)


def clone_board_file(args=None):
    """Clone board file.

    Creates a copy of the board file with all card ids replaced by new ids.

    This is the console script version taking its parameters either
    from a string provided as `args`, or from the command line:

    usage: clone_board_file [-h] src dst

    positional arguments:
      src         The board file to clone.
      dst         The name of the cloned board file.

    optional arguments:
      -h, --help  show this help message and exit

    Parameters
    ----------
    args : str, None, optional
        The string containing the arguments.

    Returns
    -------

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='The board file to clone.')
    parser.add_argument('dst', help='The name of the cloned board file.')
    args = parser.parse_args(args)

    clone_board_file_(src=args.src, dst=args.dst)


def clone_tree(args=None):
    """Clone directory tree.

    Creates a copy of a directory tree and assigns new ids to all cards
    in all board files in the copy of the tree.
    Then replaces all old card ids with these new card ids
    in all notebook and text files in the copy of the tree.

    Note that the parent directory where the root of the cloned tree will
    be placed should already exist, but not the root of the cloned directory
    tree itself.

    This is the console script version taking its parameters either
    from a string provided as `args`, or from the command line:

    usage: clone_tree [-h] [--symlinks] [--ignore [IGNORE [IGNORE ...]]]
                      [--ignore_dangling_symlinks]
                      src dst

    positional arguments:
      src                   The root of the directory tree to clone.
      dst                   The root of the cloned directory tree.

    optional arguments:
      -h, --help            show this help message and exit
      --symlinks            Copy symbolic links as symbolic links.
      --ignore [IGNORE [IGNORE ...]]
                            A list of file patterns to ignore.
      --ignore_dangling_symlinks
                            Ignore dangling symbolic links.

    Parameters
    ----------
    args : str, None, optional
        The string containing the arguments.

    Returns
    -------

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='The root of the directory tree to clone.')
    parser.add_argument('dst', help='The root of the cloned directory tree.')
    parser.add_argument('--symlinks', action='store_true', default=False, help='Copy symbolic links as symbolic links.')
    parser.add_argument('--ignore', action='store', nargs='*', default=None, help='A list of file patterns to ignore.')
    parser.add_argument('--ignore_dangling_symlinks', action='store_true', default=False, help='Ignore dangling symbolic links.')
    args = parser.parse_args(args)

    clone_tree_(src=args.src, dst=args.dst, symlinks=args.symlinks, ignore=args.ignore, ignore_dangling_symlinks=args.ignore_dangling_symlinks)
