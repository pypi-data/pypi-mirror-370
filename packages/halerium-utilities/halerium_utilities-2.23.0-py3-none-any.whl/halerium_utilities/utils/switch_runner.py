import os
from copy import deepcopy

from halerium_utilities.board import Board


def switch_runner(board: Board,
                  old_runner_id: str = None,
                  new_runner_id: str = None,
                  in_place=True) -> Board:
    """
    Switches the runner ids in setup cards for a given Board.

    Parameters
    ----------
    board: Board
        The Halerium Board instance in which to switch the runners.
    old_runner_id: str
        The runner id to be replaced. If not specified, all runner ids will be replaced.
    new_runner_id: str
        The new runner id to be inserted. If not specified, the current runner id will be used.
        The current runner is only available on a Halerium runner.
    in_place: bool
        Whether to do the replacement in-place.

    Returns
    -------
    Board

    """
    if not in_place:
        board = deepcopy(board)

    # use current runner id if None is provided
    if new_runner_id is None:
        new_runner_id = os.getenv('HALERIUM_ID', None)

    # loop through the carsd
    for card in board.cards:
        if card.type == "setup":
            _setup_args = card.type_specific.setup_args
            _runner_id = _setup_args.get("runner_id", None)
            # for every setup card with a runner_id replace it if
            # the runner_id matches the defined old_runner_id or if old_runner_id was not specified
            if _runner_id and (not old_runner_id or old_runner_id == _runner_id):
                # do not replace if new_runner_id is None
                _setup_args["runner_id"] = new_runner_id if new_runner_id else _runner_id

    return board

