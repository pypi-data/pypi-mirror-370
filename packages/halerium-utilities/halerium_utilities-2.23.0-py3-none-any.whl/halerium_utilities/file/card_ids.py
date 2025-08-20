import logging
import uuid

from copy import deepcopy


from .io import (read_board, write_board, read_notebook, write_notebook,
                 read_text_file, write_text_file,
                 get_board_notebook_and_text_filenames_in_tree)
from ..board import Board
from ..notebook.convert import convert_to_native_format, convert_to_jupyter_format


def _updated_id(old_id, new_id_for_old_id):
    """Update ids.

    Parameters
    ----------
    old_id :
        Id to update.
    new_id_for_old_id :
        Dictionary giving new keys ids old ids.

    Returns
    -------
    new_id :
        The updated id.

    """
    new_id = old_id
    while new_id in new_id_for_old_id.keys():
        new_id = new_id_for_old_id[new_id]
    return new_id


def error_handler(function):
    def handled_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as exc:
            logging.warning(f"{function.__name__} with arguments {args}, {kwargs} failed with {exc}")
    return handled_function


def create_card_id():
    return str(uuid.uuid4())


def assign_new_card_ids_to_board(board: Board, new_id_for_old_id, inplace=False):
    """Assign new ids to cards in board.

    Parameters
    ----------
    board :
        The board for which to assign new card ids.
    new_id_for_old_id :
        A dictionary for recording the mapping from old ids to new ids.
    inplace :
        Whether to assign ids in place.

    Returns
    -------
    board :
        The board with new ids.

    """
    if not inplace:
        board = deepcopy(board)

    for node in board.cards:
        old_id = node.id
        new_id = str(uuid.uuid4())
        node.id = new_id

        new_id_for_old_id[old_id] = new_id

    for edge in board.connections:
        edge.id = str(uuid.uuid4())
        old_id = edge.connections.source.id
        edge.connections.source.id = new_id_for_old_id.get(old_id, old_id)

        old_id = edge.connections.target.id
        edge.connections.target.id = new_id_for_old_id.get(old_id, old_id)
        
    for workflow in board._workflows:
        workflow.id = str(uuid.uuid4())
        # replace linked node id for main prompt field
        if workflow.linkedNodeId:
            workflow.linkedNodeId = new_id_for_old_id.get(
                        workflow.linkedNodeId, workflow.linkedNodeId)

        for element in workflow.linearTasks:
            element.id = str(uuid.uuid4())
            if element.type in ("note", "bot"):
                if (hasattr(element.type_specific, 'linkedNodeId')
                    and element.type_specific.linkedNodeId is not None
                ):
                    old_id = element.type_specific.linkedNodeId
                    element.type_specific.linkedNodeId = new_id_for_old_id.get(
                        old_id, old_id
                    )
            elif element.type == "action-chain":
                if (hasattr(element.type_specific, 'actions')
                    and isinstance(element.type_specific.actions, list)
                ):
                    for action in element.type_specific.actions:
                        if (hasattr(action, 'nodeId')
                            and action.nodeId is not None
                        ):
                            old_id = action.nodeId
                            action.nodeId = new_id_for_old_id.get(
                                old_id, old_id
                            )
            elif element.type == "upload":
                if (hasattr(element.type_specific, 'filePathTargets')
                    and isinstance(element.type_specific.filePathTargets, list)
                ):
                    for target in element.type_specific.filePathTargets:
                        if (hasattr(target, 'targetId') and
                                hasattr(target, 'targetType') and
                                target.targetType == "card" and
                                target.targetId is not None):
                            old_id = target.targetId
                            target.targetId = new_id_for_old_id.get(
                                old_id, old_id
                            )
                if (hasattr(element.type_specific, 'fileContentTargets')
                    and isinstance(element.type_specific.fileContentTargets, list)
                ):
                    for target in element.type_specific.fileContentTargets:
                        if (hasattr(target, 'targetId') and
                                hasattr(target, 'targetType') and
                                target.targetType == "card" and
                                target.targetId is not None):
                            old_id = target.targetId
                            target.targetId = new_id_for_old_id.get(
                                old_id, old_id
                            )

    return board


def replace_card_ids_in_notebook(notebook, new_id_for_old_id, inplace=False):
    """Replace card ids in notebook.

    Parameters
    ----------
    notebook :
        The notebook in which to replace card ids.
    new_id_for_old_id :
        The mapping from old ids to new ids.
    inplace :
        Whether to replace ids in place.

    Returns
    -------
    notebook :
        The notebook with the card ids replaced.

    """
    if not inplace:
        notebook = deepcopy(notebook)

    notebook = convert_to_jupyter_format(notebook, inplace=True)

    for cell in notebook["cells"]:
        replace_card_ids_in_text(cell["source"], new_id_for_old_id, inplace=True)

    notebook = convert_to_native_format(notebook, inplace=True)

    return notebook


def replace_card_ids_in_text(lines, new_id_for_old_id, inplace=False):
    """Replace card ids in text.

    Parameters
    ----------
    lines :
        The text as list of lines in which to replace card ids.
    new_id_for_old_id :
        The mapping from olds ids to new ids.
    inplace :
        Whether to replace ids in place.

    Returns
    -------
    lines:
        The text as list of lines with the card ids replaced.

    """
    if not inplace:
        lines = deepcopy(lines)

    open_tag_start = '# <halerium id="'
    close_tag_start = '# </halerium id="'
    output_tag_start = '<halerium-output id="'

    for line_number, line in enumerate(lines):
        if open_tag_start in line:
            tag = open_tag_start
        elif close_tag_start in line:
            tag = close_tag_start
        elif output_tag_start in line:
            tag = output_tag_start
        else:
            tag = None

        if tag:
            id_start = line.index(tag) + len(tag)
            try:
                id_end = line[id_start:].index('"') + id_start
                old_id = line[id_start:id_end]
                old_id = str(uuid.UUID(old_id, version=4)) # ensure valid uuid4
            except ValueError: # could be that the closing " was not found or that id invalid
                raise ValueError(f"Cannot interpret special comment line {line_number}: {line}")

            prefix = line[:id_start]
            suffix = line[id_end:]

            new_id = _updated_id(old_id, new_id_for_old_id)
            lines[line_number] = prefix + new_id + suffix

    return lines


def assign_new_card_ids_to_board_file(board_file, new_board_file, new_id_for_old_id):
    """Assign new card ids to board file.
    
    Parameters
    ----------
    board_file :
        The file to read the board from.
    new_board_file :
        The file to write the board with the new ids to.
    new_id_for_old_id :
        The dictionary for recording the mapping from old ids to new ids.

    Returns
    -------

    """
    board = read_board(board_file)
    board = assign_new_card_ids_to_board(board, new_id_for_old_id=new_id_for_old_id, inplace=True)
    write_board(board, new_board_file)


def replace_card_ids_in_notebook_file(notebook_file, new_notebook_file, new_id_for_old_id):
    """Replace card ids in notebook file.

    Parameters
    ----------
    notebook_file :
        The file to read the notebook from.
    new_notebook_file :
        The file to write the notebook with replaced ids to.
    new_id_for_old_id :
        The mapping from old ids to new ids.

    Returns
    -------

    """
    notebook = read_notebook(notebook_file)
    notebook = replace_card_ids_in_notebook(notebook, new_id_for_old_id=new_id_for_old_id, inplace=True)
    write_notebook(notebook, new_notebook_file)


def replace_card_ids_in_text_file(text_file, new_text_file, new_id_for_old_id):
    """Replace card ids in text file.

    Parameters
    ----------
    text_file :
        The file to read the text from.
    new_text_file :
        The file to write the text with replaced ids to.
    new_id_for_old_id :
        The mapping from old ids to new ids.

    Returns
    -------

    """
    lines = read_text_file(text_file)
    lines = replace_card_ids_in_text(lines, new_id_for_old_id=new_id_for_old_id, inplace=True)
    write_text_file(lines, new_text_file)


def assign_new_card_ids_to_files(board_files, notebook_files, text_files,
                                 new_board_files=None, new_notebook_files=None, new_text_files=None):
    """Assign new card ids to file.

    Assign new ids to all cards in all boards in board files.
    Then replace all old card ids with these new card ids
    in the notebook and text files provided.
    If new board, notebook, or text files are provided, the results are written
    there. Otherwise, the ids are replaced in-place.

    Parameters
    ----------
    board_files :
        The list of board files.
    notebook_files :
        The list of notebook files.
    text_files :
        The list of text files.
    new_board_files :
        The list of files to write boards with new card ids to.
        If omitted, files written to are the same as read from.
    new_notebook_files :
        The list of files to write notebooks with new card ids to.
        If omitted, files written to are the same as read from.
    new_text_files :
        The list of files to write texts with new card ids to.
        If omitted, files written to are the same as read from.

    """
    new_board_files = new_board_files or board_files
    new_notebook_files = new_notebook_files or notebook_files
    new_text_files = new_text_files or text_files

    new_id_for_old_id = dict()

    for board_file, new_board_file in zip(board_files, new_board_files):
        error_handler(assign_new_card_ids_to_board_file)(
            board_file, new_board_file, new_id_for_old_id)

    for notebook_file, new_notebook_file in zip(notebook_files, new_notebook_files):
        error_handler(replace_card_ids_in_notebook_file)(
            notebook_file, new_notebook_file, new_id_for_old_id)

    for text_file, new_text_file in zip(text_files, new_text_files):
        error_handler(replace_card_ids_in_text_file)(
            text_file, new_text_file, new_id_for_old_id)


def assign_new_card_ids_to_tree(path, include_symlinks=False):
    """Assign new card ids to all files in directory tree.

    Assign new ids to all cards in all board files in a directory tree.
    Then replace all old card ids with these new card ids
    in all notebook and text files in the tree.
    The ids are replaced in-place.

    Parameters
    ----------
    path :
        The root of the directory tree.
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
    board_filenames, notebook_filenames, text_filenames = \
        get_board_notebook_and_text_filenames_in_tree(path, include_symlinks=include_symlinks)
    assign_new_card_ids_to_files(board_filenames, notebook_filenames, text_filenames)

    return board_filenames, notebook_filenames, text_filenames


def get_duplicated_ids_in_board(board):
    """Get all duplicated IDs in a board.

    Parameters
    ----------
    board :
        The board.

    Returns
    -------
    node_duplicates : set
        The card IDs that occur more than once.
    edge_duplicates : set
        The connection IDs that occur more than once.

    """

    # check nodes
    node_id_cache = set()
    node_duplicates = set()
    for node in board.cards:
        nid = node.id
        if nid in node_id_cache:
            node_duplicates.add(nid)
        else:
            node_id_cache.add(nid)

    # check edges
    edge_id_cache = set()
    edge_duplicates = set()
    for edge in board.connections:
        eid = edge.id
        if eid in edge_id_cache:
            edge_duplicates.add(eid)
        else:
            edge_id_cache.add(eid)

    return node_duplicates, edge_duplicates


def get_duplicated_ids_in_board_file(board_file):
    """Get all duplicated IDs in a board file.

    Parameters
    ----------
    board_file :
        The file to read the board from.

    Returns
    -------
    node_duplicates : set
        The card IDs that occur more than once.
    edge_duplicates : set
        The connection IDs that occur more than once.

    """

    board = read_board(board_file)

    return get_duplicated_ids_in_board(board)


def get_duplicated_ids_in_board_file_tree(path, include_symlinks=False):
    """Get all board files with duplicated IDs in path.

    Parameters
    ----------
    path :
        The root of the directory tree.
    include_symlinks :
        Whether to include symbolic links.
        The default is `False`.

    Returns
    -------
    boards_with_duplicates : list
        Board paths containing duplicate IDs.
    skipped : list
        Board paths where the check failed.

    """
    board_filenames, notebook_filenames, text_filenames = \
        get_board_notebook_and_text_filenames_in_tree(
            path, include_symlinks=include_symlinks)

    boards_with_duplicates = []
    not_checkable = []
    for board_file in board_filenames:
        try:
            duplicates = get_duplicated_ids_in_board_file(board_file)
            if any([len(d) for d in duplicates]):
                boards_with_duplicates.append(board_file)
        except:
            not_checkable.append(board_file)

    return boards_with_duplicates, not_checkable


def deduplicate_cards_in_board(board, inplace=False, repair=True):
    """Deduplicate cards.

    All cards in the board are checked for duplicate IDs.
    Cards with duplicate IDs are either deleted or assigned
    new IDs. The latter only happens if repair=True and if the
    content of the cards is not the same.
    Connections with duplicate IDs are removed as well.

    Parameters
    ----------
    board :
        The board
    inplace :
        Whether to change the board in place.
    repair :
        Whether to assign new IDs (True) or delete (False)
        cards with duplicate IDs but different content.

    Returns
    -------
    board :
        The deduplicated board.

    """

    if not inplace:
        board = deepcopy(board)

    # check nodes
    node_dict = {}
    for i in range(len(board.cards)-1, -1, -1):
        node = board.cards[i]
        node_id = node.id
        if node_id in node_dict:
            if repair and (node != node_dict[node_id]):
                # if repair=True and the node is not a duplicate
                # assign a new id instead of deleting
                new_id = str(uuid.uuid4())
                node.id = new_id
                node_dict[new_id] = node
            else:
                # otherwise delete the node
                board.cards.pop(i)
        else:
            node_dict[node_id] = node

    edge_dict = {}
    for i in range(len(board.connections)-1, -1, -1):
        edge = board.connections[i]
        edge_id = edge.id
        if edge_id in edge_dict:
            if repair and (edge != edge_dict[edge_id]):
                new_id = str(uuid.uuid4())
                edge.id = new_id
                edge_dict[new_id] = edge
            else:
                board.connections.pop(i)
        else:
            edge_dict[edge_id] = edge

    return board


def deduplicate_cards_in_board_file(board_file, new_board_file, repair=True):
    """Deduplicate cards in board file.

    All cards in the board are checked for duplicate IDs.
    Cards with duplicate IDs are either deleted or assigned
    new IDs. The latter only happens if repair=True and if the
    content of the cards is not the same.
    Connections with duplicate IDs are removed as well.

    Parameters
    ----------
    board_file :
        The file to read the board from.
    new_board_file :
        The file to write the board with the deduplicated cards to.
    repair :
        Whether to assign new IDs (True) or delete (False)
        cards with duplicate IDs but different content.

    Returns
    -------
    """

    board = read_board(board_file)

    # avoid overwriting in-place board if not necessary
    if board_file == new_board_file:
        duplicate_cards, duplicate_connections = (
            get_duplicated_ids_in_board(board))
        if len(duplicate_cards) == len(duplicate_connections) == 0:
            return False

    board = deduplicate_cards_in_board(board,
                                       inplace=True, repair=repair)

    write_board(board, new_board_file)

    return True


def deduplicate_cards_in_board_file_tree(path, repair=True, include_symlinks=False):
    """Deduplicate cards for all boards in file tree.

    Parameters
    ----------
    path :
        The root of the directory tree.
    repair :
        Whether to assign new IDs (True) or delete (False)
        cards with duplicate IDs but different content.
    include_symlinks :
        Whether to include symbolic links.
        The default is `False`.

    Returns
    -------
    changed_boards : list
        Board paths were deduplication was done.
    not_checkable : list
        Board paths where the check failed.
    """
    board_filenames, notebook_filenames, text_filenames = \
        get_board_notebook_and_text_filenames_in_tree(
            path, include_symlinks=include_symlinks)

    changed_boards = []
    not_checkable = []
    for board_file in board_filenames:
        try:
            callback = deduplicate_cards_in_board_file(board_file, board_file, repair=repair)
            if callback:
                changed_boards.append(board_file)
        except:
            not_checkable.append(board_file)

    return changed_boards, not_checkable
