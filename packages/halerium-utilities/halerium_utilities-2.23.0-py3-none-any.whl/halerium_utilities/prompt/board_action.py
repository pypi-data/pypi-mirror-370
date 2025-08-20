from typing import Union, Literal

from halerium_utilities.board.board import Board
from halerium_utilities.board.navigator import BoardNavigator
from halerium_utilities.prompt.agents import get_agent_answer_async, get_agent_answer


async def apply_board_action_async(board: Union[dict, Board],
                                   card_id: str, action: Literal["run", "run-tree"] = "run",
                                   board_path: str = None, user_info: dict = None,
                                   copy_actions: bool = True) -> Board:
    """
    Asynchronously executes a bot card action and returns the updated board.

    Parameters
    ----------
    board : Union[dict, Board]
        The board.
    card_id : str
        The id of the bot card to execute.
    action : Literal["run", "run-tree"]
        Whether to execute only the card or the whole prompt tree stemming from it.
    board_path: str
        The path to which stateful functions like Python kernels are assigned.
        If no path is provided than these functions are not available.
    user_info: dict, optional
        Dict with `{"username": user_email, "name": full_name}`.
        With this set the agent can utilize e.g. the "Bot knows user" setting
        and function calls by the agent can utilize user_info.
        The default is None.
    copy_actions: bool
        Whether the copy actions should be applied.
        For example the prompt_output of a bot card is copied to attached note cards.
    Returns
    -------
    Board
        the updated board with the cards modified according to the action and subsequent copy events.
    """
    board_navigator = BoardNavigator(board)

    if action == "run-tree":
        execution_ids = board_navigator.resolve_tree_execution(card_id)
    else:
        execution_ids = [card_id]

    for ex_id in execution_ids:
        outputs = await get_agent_answer_async(
            board=board.to_dict(), card_id=ex_id,
            path=board_path, user_info=user_info
        )

        card_update = {
            "id": ex_id,
            "type_specific": {
                "prompt_output": outputs["prompt_output"]
            }
        }
        attachments = outputs.get("attachments")
        if attachments:
            old_attachments = board.get_card_by_id(ex_id).type_specific.attachments
            card_update["type_specific"]["attachments"] = {**old_attachments, **attachments}

        board.update_card(card_update)

        if copy_actions:
            board_navigator = BoardNavigator(board)
            copy_updates = board_navigator.get_bot_card_copy_updates(ex_id)
            for cpu in copy_updates:
                board.update_card(cpu)

    return board


def apply_board_action(board: Union[dict, Board],
                       card_id: str, action: Literal["run", "run-tree"] = "run",
                       board_path: str = None, user_info: dict = None,
                       copy_actions: bool = True) -> Board:
    """
    Executes a bot card action and returns the updated board.

    Parameters
    ----------
    board : Union[dict, Board]
        The board.
    card_id : str
        The id of the bot card to execute.
    action : Literal["run", "run-tree"]
        Whether to execute only the card or the whole prompt tree stemming from it.
    board_path: str
        The path to which stateful functions like Python kernels are assigned.
        If no path is provided than these functions are not available.
    user_info: dict, optional
        Dict with `{"username": user_email, "name": full_name}`.
        With this set the agent can utilize e.g. the "Bot knows user" setting
        and function calls by the agent can utilize user_info.
        The default is None.
    copy_actions: bool
        Whether the copy actions should be applied.
        For example the prompt_output of a bot card is copied to attached note cards.
    Returns
    -------
    Board
        the updated board with the cards modified according to the action and subsequent copy events.
    """
    board_navigator = BoardNavigator(board)

    if action == "run-tree":
        execution_ids = board_navigator.resolve_tree_execution(card_id)
    else:
        execution_ids = [card_id]

    for ex_id in execution_ids:
        outputs = get_agent_answer(
            board=board.to_dict(), card_id=ex_id,
            path=board_path, user_info=user_info
        )

        card_update = {
            "id": ex_id,
            "type_specific": {
                "prompt_output": outputs["prompt_output"]
            }
        }
        attachments = outputs.get("attachments")
        if attachments:
            old_attachments = board.get_card_by_id(ex_id).type_specific.attachments
            card_update["type_specific"]["attachments"] = {**old_attachments, **attachments}

        board.update_card(card_update)

        if copy_actions:
            board_navigator = BoardNavigator(board)
            copy_updates = board_navigator.get_bot_card_copy_updates(ex_id)
            for cpu in copy_updates:
                board.update_card(cpu)

    return board
