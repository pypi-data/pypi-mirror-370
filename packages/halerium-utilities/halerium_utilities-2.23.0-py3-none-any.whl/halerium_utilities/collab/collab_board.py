import httpx
import logging
import os
from pathlib import Path
from typing import Any, Dict, Union
from urllib.parse import urljoin, quote

from halerium_utilities.board.board import Board
from halerium_utilities.board import schemas
from halerium_utilities.collab import schemas as collab_schemas
from halerium_utilities.logging.exceptions import (
    BoardConnectionError, DuplicateIdError, BoardUpdateError, IdNotFoundError)


class CollabBoard(Board):
    """
    Extension of the board class to communicate with the collaboration server.

    The class provides additional pull and push methods to keep the in-memory
    board in sync with the one of the collaboration server. The class is designed
    to be used on a runner but can be initialized elsewhere as well with the
    optional arguments in the init.
    """

    def __init__(self, path: Union[str, Path, os.PathLike],
                 url: str = None, headers: Dict[str, Any] = None,
                 pull_on_init=True,
                 check_if_path_exists=True):
        """
        Initialize a CollabBoard instance.

        Parameters
        ----------
        path : Union[str, Path, os.PathLike]
            The path to the board file.
        url : str, optional
            The URL of the collaboration server. If not provided, it will be constructed from environment variables.
        headers : Dict[str, Any], optional
            The headers to use for HTTP requests. If not provided, it will be constructed from environment variables.
        pull_on_init : bool, optional
            Whether to pull the board from the collaboration server upon initialization. Defaults to True.
        check_if_path_exists : bool, optional
            Whether to check if the board file exists at the specified path. Defaults to True.
        """

        self.file_path = Path(path)
        if check_if_path_exists:
            if not self.file_path.exists():
                raise FileNotFoundError(f"{self.file_path} could not be found.")
            if not self.file_path.suffix == ".board":
                raise ValueError(".board file expected.")

        if url is None:
            tenant = os.getenv('HALERIUM_TENANT_KEY', '')
            workspace = os.getenv('HALERIUM_PROJECT_ID', '')
            runner_id = os.getenv('HALERIUM_ID', '')
            base_url = os.getenv('HALERIUM_BASE_URL', '')

            path_from_home = self.file_path.resolve().relative_to(self.file_path.home()).as_posix()

            url = urljoin(base_url,
                          f"/api/tenants/{quote(tenant, safe='')}"
                          f"/projects/{quote(workspace, safe='')}"
                          f"/runners/{quote(runner_id, safe='')}"
                          "/collab/boards/" +
                          quote(path_from_home, safe=''))
        self.url = url

        if headers is None:
            headers = {'halerium-runner-token': os.getenv('HALERIUM_TOKEN', '')}
        self.headers = headers

        self._actions = []

        super().__init__(board=None)

        if pull_on_init:
            self.pull()

    def __eq__(self, other):
        """
        Check equality between two CollabBoard instances.

        Parameters
        ----------
        other : CollabBoard
            The other CollabBoard instance to compare with.

        Returns
        -------
        bool
            True if both instances are equal, False otherwise.
        """
        if isinstance(other, CollabBoard):
            return (self._board == other._board and
                    self._actions == other._actions)
        return False

    def _reapply_actions(self):
        for action in self._actions:
            try:
                if action.type == "add_node":
                    super().add_card(action.payload.dict(exclude_none=True))
                elif action.type == "add_edge":
                    super().add_connection(action.payload.dict(exclude_none=True))
                elif action.type == "remove_node":
                    super().remove_card(action.payload.dict(exclude_none=True))
                elif action.type == "remove_edge":
                    super().remove_connection(action.payload.dict(exclude_none=True))
                elif action.type == "update_node":
                    super().update_card(action.payload.dict(exclude_none=True))
                elif action.type == "update_edge":
                    super().update_connection(action.payload.dict(exclude_none=True))
                elif action.type == "update_process_queue":
                    pass
                else:
                    raise TypeError(f"Unknown action type {action.type}.")
            except (BoardConnectionError, BoardUpdateError,
                    IdNotFoundError, DuplicateIdError) as exc:
                logging.warning(f"Action {action} could not be applied ({exc}).")

    def pull(self):
        """
        Pull the latest board data from the collaboration server and update the in-memory board.
        """
        with httpx.Client() as httpx_client:
            response = httpx_client.get(self.url,
                                        headers=self.headers)
        response.raise_for_status()
        board_dict = response.json()["data"]
        self._board = schemas.Board.validate(board_dict)

    async def pull_async(self):
        """
        Asynchronously pull the latest board data from the collaboration server and update the in-memory board.
        """
        async with httpx.AsyncClient() as httpx_client:
            response = await httpx_client.get(self.url,
                                              headers=self.headers)
        response.raise_for_status()
        board_dict = response.json()["data"]
        self._board = schemas.Board.validate(board_dict)

    def _prepare_actions_data(self):
        data = collab_schemas.BoardActions.validate(
            {"actions": self._actions}).dict(exclude_none=True)
        return data

    def _flush_actions(self):
        self._actions = []

    def push(self):
        """
        Push the local changes to the collaboration server.
        """
        if len(self._actions) == 0:
            return None

        data = self._prepare_actions_data()
        with httpx.Client() as httpx_client:
            response = httpx_client.post(self.url,
                                         headers=self.headers,
                                         json=data)
        response.raise_for_status()
        self._flush_actions()

    async def push_async(self):
        """
        Asynchronously push the local changes to the collaboration server.
        """
        if len(self._actions) == 0:
            return None

        data = self._prepare_actions_data()
        async with httpx.AsyncClient() as httpx_client:
            response = await httpx_client.post(self.url,
                                               headers=self.headers,
                                               json=data)
        response.raise_for_status()
        self._flush_actions()

    def add_card(self, card: Union[dict, schemas.Node]):
        """
        Add a card (node) to the board and queue the action for pushing to the collaboration server.

        Parameters
        ----------
        card : Union[dict, schemas.Node]
            The card data to add. Can be a dictionary or a Node schema object.
        """
        if not isinstance(card, schemas.Node):
            card = schemas.Node.validate(card)
        action = collab_schemas.BoardAction.validate(
            {"type": "add_node",
             "payload": card}
        )
        super().add_card(card)
        self._actions.append(action)
    add_card.__doc__ = Board.add_card.__doc__

    def add_connection(self, connection: Union[dict, schemas.Edge]):
        """
        Add a connection (edge) to the board and queue the action for pushing to the collaboration server.

        Parameters
        ----------
        connection : Union[dict, schemas.Edge]
            The connection data to add. Can be a dictionary or an Edge schema object.
        """
        if not isinstance(connection, schemas.Edge):
            connection = schemas.Edge.validate(connection)
        action = collab_schemas.BoardAction.validate(
            {"type": "add_edge",
             "payload": connection}
        )
        super().add_connection(connection)
        self._actions.append(action)
    add_connection.__doc__ = Board.add_connection.__doc__

    def _prep_index(self, index, max_index):
        if index is None:
            index = len(self.path_elements)
        index = int(index)
        if index < 0:
            raise ValueError("Negative indices are not supported.")
        index = min(max_index, index)
        return index

    def add_path_element(self, element: Union[dict, schemas.PathElement],
                         index: int = None):
        if not isinstance(element, schemas.PathElement):
            element = schemas.PathElement.validate(element)

        index = self._prep_index(index, len(self.path_elements))

        insert = {
            "type": "insert_task",
            "payload": {"workflowId": self.path.id, 
                        "task": element.dict(),
                        "index": index}
        }

        super().add_path_element(element, index=index)
        self._actions.append(insert)
    add_path_element.__doc__ = Board.add_path_element.__doc__

    def remove_path_element(self, element: Union[Dict, schemas.PathElement]):
        if not isinstance(element, schemas.PathElement):
            element = schemas.id_schema.ElementId.validate(element)

        remove = {
            "type": "remove_task",
            "payload": {"workflowId": self.path.id, 
                        "task": {
                                    "id": element.id,
                        }
            }
        }

        super().remove_path_element(element)
        self._actions.append(remove)
    remove_path_element.__doc__ = Board.remove_path_element.__doc__

    def move_path_element(self, element: Union[Dict, schemas.PathElement], index: int):
        if not isinstance(element, schemas.PathElement):
            element = schemas.ElementId.validate(element)

        element = self.get_path_element_by_id(element.id)

        index = self._prep_index(index, len(self.path_elements)-1)

        remove = {
            "type": "remove_task",
            "payload": {"workflowId": self.path.id,
                        "task": {
                            "id": element.id,
                        }}
        }

        insert = {
            "type": "insert_task",
            "payload": {"workflowId": self.path.id,
                        "task": element.dict(),
                        "index": index}
        }

        super().move_path_element(element, index)
        self._actions.append(remove)
        self._actions.append(insert)
    move_path_element.__doc__ = Board.move_path_element.__doc__

    def update_path_element(self, element_update: Union[Dict, schemas.PathElementUpdate]):
        if not isinstance(element_update, schemas.PathElementUpdate):
            if "type" not in element_update:
                element_update["type"] = self.get_path_element_by_id(element_update["id"]).type
            element_update = schemas.PathElementUpdate.validate(element_update)
            
        update = {
            "type": "update_task",
            "payload": {"workflowId": self.path.id,
                        "task": element_update.dict(exclude_none=True)
                }
        }

        super().update_path_element(element_update)
        self._actions.append(update)
    update_path_element.__doc__ = Board.update_path_element.__doc__

    def remove_card(self, card: Union[Dict, schemas.Node]):
        """
        Remove a card (node) from the board and queue the action for pushing to the collaboration server.

        Parameters
        ----------
        card : Union[Dict, schemas.Node]
            The card to remove. Can be a dictionary with the card ID or a Node schema object.
        """
        if not isinstance(card, schemas.id_schema.NodeId):
            card = schemas.id_schema.NodeId.validate(card)
        card_id = card.id
        action = collab_schemas.BoardAction.validate(
            {"type": "remove_node",
             "payload": {"id": card_id}}
        )
        super().remove_card(card)
        self._actions.append(action)
    remove_card.__doc__ = Board.remove_card.__doc__

    def remove_connection(self, connection: Union[Dict, schemas.Edge]):
        """
        Remove a connection (edge) from the board and queue the action for pushing to the collaboration server.

        Parameters
        ----------
        connection : Union[Dict, schemas.Edge]
            The connection to remove. Can be a dictionary with the connection ID or an Edge schema object.
        """
        if not isinstance(connection, schemas.id_schema.EdgeId):
            connection = schemas.id_schema.EdgeId.validate(connection)
        connection_id = connection.id
        action = collab_schemas.BoardAction.validate(
            {"type": "remove_edge",
             "payload": {"id": connection_id}}
        )
        super().remove_connection(connection)
        self._actions.append(action)
    remove_connection.__doc__ = Board.remove_connection.__doc__

    def update_card(self, card_update: Union[Dict, schemas.NodeUpdate]):
        """
        Update a card (node) on the board and queue the action for pushing to the collaboration server.

        Parameters
        ----------
        card_update : Union[Dict, schemas.NodeUpdate]
            The card update data. Can be a dictionary or a NodeUpdate schema object.
        """
        if not isinstance(card_update, schemas.NodeUpdate):
            if "type" not in card_update:
                card_update["type"] = self.get_card_by_id(card_update["id"]).type
            card_update = schemas.NodeUpdate.validate(card_update)

        action = collab_schemas.BoardAction.validate(
            {"type": "update_node",
             "payload": card_update.dict(exclude_none=True)}
            # TODO: if the update includes a partial position update, e.g. `"position": {"x": 100}`
            # the y-position will get lost on the server side -> patch the old y position in as a workaround.
        )
        super().update_card(card_update)
        self._actions.append(action)
    update_card.__doc__ = Board.update_card.__doc__

    def update_connection(self, connection_update: Union[Dict, schemas.EdgeUpdate]):
        """
        Update a connection (edge) on the board and queue the action for pushing to the collaboration server.

        Parameters
        ----------
        connection_update : Union[Dict, schemas.EdgeUpdate]
            The connection update data. Can be a dictionary or an EdgeUpdate schema object.
        """
        if not isinstance(connection_update, schemas.EdgeUpdate):
            if "type" not in connection_update:
                connection_update["type"] = self.get_connection_by_id(
                    connection_update["id"]).type
            connection_update = schemas.EdgeUpdate.validate(connection_update)

        action = collab_schemas.BoardAction.validate(
            {"type": "update_edge",
             "payload": connection_update.dict(exclude_none=True)}
        )
        super().update_connection(connection_update)
        self._actions.append(action)
    update_connection.__doc__ = Board.update_connection.__doc__

    def update_process_queue(
            self, process_queue_update: Union[Dict, collab_schemas.ProcessQueueUpdate]):
        """
        Update the processing queue for prompt evaluations.
        This method does not work for jupyter-kernel agents.

        Parameters
        ----------
        process_queue_update : Union[Dict, collab_schemas.ProcessQueueUpdate]):
            The pattern is `{"id": node_id, "continue_prompt": bool, "end": bool}`.
            The "continue_prompt" parameter governs whether to continue the prompt process.
            The "end" parameter governs whether to push to the end (true) or the beginning (false) of the queue.
        """
        # if isinstance(process_queue_update, collab_schemas.ProcessQueueUpdate):
        #     process_queue_update = process_queue_update.dict(exclude_none=True)
        action = collab_schemas.BoardAction.validate(
            {"type": "update_process_queue",
             "payload": process_queue_update}
        )
        self._actions.append(action)

    def queue_execution(self, card: Union[Dict, schemas.Node]):
        """
        Queue a card for execution. This method works for all agents.

        Parameters
        ----------
        card : Union[Dict, schemas.Node]
            The pattern is `{"id": node_id}`.
        """
        action = collab_schemas.BoardAction.validate(
            {"type": "send_node_to_execute",
             "payload": card}
        )
        self._actions.append(action)

