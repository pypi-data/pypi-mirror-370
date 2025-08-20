from typing import Union

from halerium_utilities.board.board import Board
from halerium_utilities.board.navigator import BoardNavigator
from halerium_utilities.prompt.agents import get_agent_answer_async, get_agent_answer

from halerium_utilities.prompt.board_action import apply_board_action, apply_board_action_async


async def apply_path_action_async(board: Union[dict, Board, BoardNavigator],
                                  element_id: str, board_path: str = None,
                                  user_info: dict = None) -> Board:
    """
    Executes a path action element and returns the updated board.

    Parameters
    ----------
    board : Union[dict, Board, BoardNavigator]
        The board.
    element_id : str
        The id of the action element.
    board_path: str
        The path to which stateful functions like Python kernels are assigned.
        If no path is provided than these functions are not available.
    user_info: dict, optional
        Dict with `{"username": user_email, "name": full_name}`.
        With this set the agent can utilize e.g. the "Bot knows user" setting
        and function calls by the agent can utilize user_info.
        The default is None.

    Returns
    -------
    Board
        the board with the cards modified according to the action chain
    """
    board_navigator = BoardNavigator(board)
    execution_ids = board_navigator.get_action_element_executions(element_id)

    updated_board = Board(board)
    for ex_id in execution_ids:
        updated_board = await apply_board_action_async(
            updated_board, ex_id, action="run", board_path=board_path,
            user_info=user_info, copy_actions=True
        )

    return updated_board


def apply_path_action(board: Union[dict, Board],
                      element_id: str, board_path: str = None,
                      user_info: dict = None) -> Board:
    """
    Executes a path action element and returns the updated board.

    Parameters
    ----------
    board : Union[dict, Board, BoardNavigator]
        The board.
    element_id : str
        The id of the action element.
    board_path: str
        The path to which stateful functions like Python kernels are assigned.
        If no path is provided than these functions are not available.
    user_info: dict, optional
        Dict with `{"username": user_email, "name": full_name}`.
        With this set the agent can utilize e.g. the "Bot knows user" setting
        and function calls by the agent can utilize user_info.
        The default is None.

    Returns
    -------
    Board
        the board with the cards modified according to the action chain
    """
    board_navigator = BoardNavigator(board)
    execution_ids = board_navigator.get_action_element_executions(element_id)

    updated_board = Board(board)
    for ex_id in execution_ids:
        updated_board = apply_board_action(
            updated_board, ex_id, action="run", board_path=board_path,
            user_info=user_info, copy_actions=True
        )

    return updated_board
