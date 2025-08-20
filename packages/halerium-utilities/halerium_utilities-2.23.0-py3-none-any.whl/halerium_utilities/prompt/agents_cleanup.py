import httpx
import os
from urllib.parse import urljoin
from typing import Dict, Union

from halerium_utilities.board import Board, BoardNavigator


def _prepare_cleanup_request(runner_id: str,
                             path: str,
                             setup_id: str = None):

    tenant = os.getenv('HALERIUM_TENANT_KEY', '')
    workspace = os.getenv('HALERIUM_PROJECT_ID', '')
    auth_runner_id = os.getenv('HALERIUM_ID', '')
    base_url = os.getenv('HALERIUM_BASE_URL', '')
    url = urljoin(base_url, "/api"
                            f"/tenants/{tenant}"
                            f"/projects/{workspace}"
                            f"/runners/{auth_runner_id}"
                            "/prompt/runner/cleanup")

    headers = {'halerium-runner-token': os.getenv('HALERIUM_TOKEN', '')}

    payload = {"runner_id": str(runner_id), "path": str(path)}
    if setup_id:
        payload["setup_id"] = setup_id

    return dict(
        method="POST",
        url=url,
        headers=headers,
        json=payload,
        timeout=120,
    )


async def call_cleanup_async(runner_id: str,
                             path: str,
                             setup_id: str = None):
    """Call the cleanup routine asynchronously for stateful functions on a runner.

    If bots (=agents) utilize stateful functions (e.g. Python kernels) they are assigned to a specific path
    and are kept alive on the utilized runner until they are cleaned up.
    The cleanup is necessary to free up resources on a runner once a bot is done.

    Parameters
    ----------
    runner_id: str
        The runner id of the runner on which the stateful functions were started.
        This is specified in the setup card of the bot in question.
    path: str
        The path to which stateful functions like Python kernels were assigned.
    setup_id: str, optional
        The uuid of the setup card for which the stateful functions are to be cleaned up.
        If no setup_id is provided all functions for the given runner and path are cleaned up.

    Returns
    -------
    dict
        The response of the cleanup endpoint if successful.

    Examples
    --------
    >>> board = {"nodes": [...], "edges": [...]}
    >>> card_id = "[card id]"
    >>> path = "[some_path]"
    >>> gen = agents.call_agent_async(board, card_id, path)
    >>> # evaluate agent results, perhaps make additional call_agent calls with the same path
    >>> runner_id = "[runner_id]" # can be found by inspecting the type_specific content of the setup card.
    >>> await call_cleanup_async(runner_id, path)
    """

    async with httpx.AsyncClient() as httpx_client:
        response = await httpx_client.request(**_prepare_cleanup_request(runner_id, path, setup_id))
        response.raise_for_status()
        return response.json()


def call_cleanup(runner_id: str,
                 path: str,
                 setup_id: str = None):
    """Call the cleanup routine for stateful functions on a runner.

    If bots (=agents) utilize stateful functions (e.g. Python kernels) they are assigned to a specific path
    and are kept alive on the utilized runner until they are cleaned up.
    The cleanup is necessary to free up resources on a runner once a bot is done.

    Parameters
    ----------
    runner_id: str
        The runner id of the runner on which the stateful functions were started.
        This is specified in the setup card of the bot in question.
    path: str
        The path to which stateful functions like Python kernels were assigned.
    setup_id: str, optional
        The uuid of the setup card for which the stateful functions are to be cleaned up.
        If no setup_id is provided all functions for the given runner and path are cleaned up.

    Returns
    -------
    dict
        The response of the cleanup endpoint if successful.

    Examples
    --------
    >>> board = {"nodes": [...], "edges": [...]}
    >>> card_id = "[card id]"
    >>> path = "[some_path]"
    >>> gen = agents.call_agent(board, card_id, path)
    >>> # evaluate agent results, perhaps make additional call_agent calls with the same path
    >>> runner_id = "[runner_id]" # can be found by inspecting the type_specific content of the setup card.
    >>> call_cleanup(runner_id, path)
    """

    with httpx.Client() as httpx_client:
        response = httpx_client.request(**_prepare_cleanup_request(runner_id, path, setup_id))
        response.raise_for_status()
        return response.json()


def cleanup_board(board: Union[Dict, Board],
                  path: str,
                  card_id: str = None):
    """Call the cleanup routine for stateful functions used in the board.

    This method is a convenience function to the `call_cleanup` method.
    With this function the runner_id(s) are automatically extracted from the given board.
    The provided card_id does not have to be the setup card id but can be any bot card id.
    This method will automatically trace the provided card id back to its setup card to then
    execute the correct cleanup.

    Parameters
    ----------
    board: dict or Board
        The board in which the user runners are referenced in the setup cards.
    path: str
        The path to which the stateful functions were assigned to.
    card_id: str, optional
        The uuid of the card used to call the stateful functions.
        If multiple cards were used one card of the prompt tree suffices since
        the card will be traced back to the parent setup card which is common
        for the whole prompt tree.

    Returns
    -------

    """

    board_navigator = BoardNavigator(board=board)

    if card_id:
        setup_id = board_navigator.get_setup_card_id(card_id)
        runner_id = board_navigator.get_functions_runner_id(card_id)
        call_cleanup(runner_id=runner_id, path=path, setup_id=setup_id)
    else:
        runner_ids = set()
        for cid in board_navigator.cards:
            if board_navigator.is_setup_card(cid):
                runner_ids.add(board_navigator.get_functions_runner_id(cid))
        for rid in runner_ids:
            call_cleanup(runner_id=rid, path=path)


async def cleanup_board_async(board: Union[Dict, Board],
                              path: str,
                              card_id: str = None):
    """Call the asynchronous cleanup routine for stateful functions used in the board.

    This method is a convenience function to the `call_cleanup_async` method.
    With this function the runner_id(s) are automatically extracted from the given board.
    The provided card_id does not have to be the setup card id but can be any bot card id.
    This method will automatically trace the provided card id back to its setup card to then
    execute the correct cleanup.

    Parameters
    ----------
    board: dict or Board
        The board in which the user runners are referenced in the setup cards.
    path: str
        The path to which the stateful functions were assigned to.
    card_id: str, optional
        The uuid of the card used to call the stateful functions.
        If multiple cards were used one card of the prompt tree suffices since
        the card will be traced back to the parent setup card which is common
        for the whole prompt tree.

    Returns
    -------

    """

    board_navigator = BoardNavigator(board=board)

    if card_id:
        setup_id = board_navigator.get_setup_card_id(card_id)
        runner_id = board_navigator.get_functions_runner_id(card_id)
        await call_cleanup_async(runner_id=runner_id, path=path, setup_id=setup_id)
    else:
        runner_ids = set()
        for cid in board_navigator.cards:
            if board_navigator.is_setup_card(cid):
                runner_ids.add(board_navigator.get_functions_runner_id(cid))
        for rid in runner_ids:
            await call_cleanup_async(runner_id=rid, path=path)
