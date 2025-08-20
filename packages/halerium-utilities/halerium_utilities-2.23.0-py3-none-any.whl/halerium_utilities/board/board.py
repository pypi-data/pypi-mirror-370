import json
import uuid

from copy import deepcopy
from pydantic.v1.utils import deep_update
from typing import Any, Dict, List, Optional, TextIO, Union

from halerium_utilities.board._board_version import __board_version__
from halerium_utilities.board import connection_rules
from halerium_utilities.board import schemas
from halerium_utilities.logging.exceptions import (
    BoardConnectionError, DuplicateIdError, IdNotFoundError, BoardUpdateError, PathLinkError)


class Board:
    """
    Class for Halerium Boards.
    """

    __version__ = __board_version__

    def __init__(self, board: Union[Dict[str, Any], schemas.Board] = None):
        """
        Initialize the Board class with a board dict or schema instance.

        Parameters
        ----------
        board (Union[Dict[str, Any], schemas.Board]): The board.
        """
        if board is None:
            board = {"version": self.__version__,
                     "nodes": [],
                     "edges": [],
                     "workflows": [],
                     }
        if isinstance(board, Board):
            board = board.to_dict()
        self._board = schemas.Board.validate(board)
        for edge in self._board.edges:
            self.check_connection_rules(edge)

    def to_dict(self):
        """
        Return board as dictionary

        Returns
        -------
        dict: the board as a dictionary
        """
        return self._board.dict()

    def __eq__(self, other):
        if isinstance(other, Board):
            return self._board == other._board
        return False

    @classmethod
    def from_json(cls, file: Union[str, TextIO]) -> 'Board':
        """
        Create a Board instance from a JSON file or file-like object.

        Parameters
        ----------
        file : Union[str, TextIO]
            A file path as a string or a file-like object to read the JSON data from.

        Returns
        -------
        Board
            An instance of the Board class initialized with the data from the JSON.
        """
        try:
            board_dict = json.load(file)
        except AttributeError:
            with open(file, "r", encoding="utf-8") as f:
                board_dict = json.load(f)
        return cls(board_dict)

    def to_json(self, file: Optional[Union[str, TextIO]] = None) -> Optional[str]:
        """
        Serialize the Board instance to JSON and write it to a file or file-like object.
        If no file is provided, returns the JSON string.

        Parameters
        ----------
        file : Optional[Union[str, TextIO]]
            A file path as a string or a file-like object to write the JSON data to.
            If None, the method returns the JSON string instead of writing to a file.

        Returns
        -------
        Optional[str]
            The JSON string if no file is provided, otherwise None.
        """
        board_dict = self.to_dict()

        if file is None:
            return json.dumps(board_dict)

        try:
            json.dump(board_dict, file)
        except AttributeError:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(board_dict, f)

    @property
    def card_ids(self):
        return [node.id for node in self._board.nodes]

    @property
    def cards(self):
        return self._board.nodes

    @property
    def connection_ids(self):
        return [edge.id for edge in self._board.edges]

    @property
    def connections(self):
        return self._board.edges

    @property
    def _workflows(self):
        self._init_path()
        return self._board.workflows

    def _init_path(self):
        if not self._board.workflows:
            self._board.workflows.append(
                schemas.workflow.Workflow.validate({"id": str(uuid.uuid4())})
            )

    @property
    def path_element_ids(self):
        return [element.id for element in self.path_elements]

    @property
    def path(self):
        return self._workflows[0]

    @property
    def path_elements(self):
        return self.path.linearTasks

    def get_card_by_id(self, id: str):
        """
        Get a card by its id

        Parameters
        ----------
        id (str): the uuid4 of the card

        Returns
        -------
        schemas.Node: the card as a Node schema instance
        """
        for node in self._board.nodes:
            if id == node.id:
                return node
        raise IdNotFoundError(f"Card with id {id} not found.")

    def get_connection_by_id(self, id: str):
        """
        Get a connection by its id

        Parameters
        ----------
        id (str): the uuid4 of the connection

        Returns
        -------
        schemas.Edge: the connection as an Edge schema instance
        """
        for edge in self._board.edges:
            if id == edge.id:
                return edge
        raise IdNotFoundError(f"Connection with id {id} not found.")

    def get_path_element_by_id(self, id: str):
        """
        Get a path element by its id

        Parameters
        ----------
        id (str): the uuid4 of the element

        Returns
        -------
        schemas.PathElement: the card as a PathElement schema instance
        """
        for element in self.path_elements:
            if id == element.id:
                return element
        raise IdNotFoundError(f"Element with id {id} not found.")

    def resolve_path_element(self, element: Union[Dict, schemas.PathElement]):
        """
        Returns the resolved path element that updates the element's properties
        with the ones of a possibly linked card.

        Parameters
        ----------
        element (Union[Dict[str, Any], schemas.PathElement]):
            The element to resolve.

        Returns
        -------
        Dict or schemas.PathElement
            The (copied) resolved element in the same type as the input.

        """
        return_dict = False
        if isinstance(element, dict):
            return_dict = True
            resolved_element = schemas.PathElement.validate(element)
        else:
            resolved_element = deepcopy(element)

        if not hasattr(resolved_element.type_specific, "linkedNodeId"):
            return resolved_element  # immediate return for unlinkable elements

        if card_id := resolved_element.type_specific.linkedNodeId:
            new_type_specific = self.get_card_by_id(card_id).type_specific.dict()
            new_type_specific.update({"linkedNodeId": card_id})
            resolved_element.type_specific = type(resolved_element.type_specific).validate(
                new_type_specific)

        if return_dict:
            return resolved_element.dict()
        else:
            return resolved_element

    def get_all_connections_of_card(self, card_id: str, connector: str = None):
        """Return all connections from and to a card.
        Optionally filters for connections connecting to a specific connector of the card.

        Parameters
        ----------
        card_id (str): the uuid4 of the card
        connector (str, optional): The connector to which the connections must connect

        Returns
        -------
        list: list of connections
        """
        edge_list = []
        for edge in self._board.edges:
            if card_id in (edge.connections.source.id,
                           edge.connections.target.id):
                if connector:
                    for conn in (edge.connections.source, edge.connections.target):
                        if conn.connector == connector and conn.id == card_id:
                            edge_list.append(edge)
                else:
                    edge_list.append(edge)
        return edge_list

    def add_card(self, card: Union[dict, schemas.Node]):
        """
        Adds a card to the board

        Parameters
        ----------
        card (Union[Dict[str, Any], schemas.Node]): The card to add.

        Returns
        -------

        Raises
        ------
        DuplicateIdError: If the id of the card is already in use.
        """
        if not isinstance(card, schemas.Node):
            card = schemas.Node.validate(card)

        if card.id in self.card_ids:
            raise DuplicateIdError("Duplicate node id detected.")

        self._board.nodes.append(card)

    def remove_card(self, card: Union[Dict, schemas.Node]):
        """
        Removes a card.

        Automatically removes all connections from and to that card as well.

        Parameters
        ----------
        card (Union[Dict, schemas.Node]):
            The card to remove or a dict with {"id": card_id}

        Returns
        -------

        Raises
        ------
        IdNotFoundError: If the id of the card could not be found.
        """
        if not isinstance(card, schemas.id_schema.NodeId):
            card = schemas.id_schema.NodeId.validate(card)
        card_id = card.id

        for index in range(len(self.cards)-1, -1, -1):
            if self.cards[index].id == card_id:
                self._remove_all_connections_to_card_id(card_id)
                self.cards.pop(index)
                return None
        raise IdNotFoundError("Card not found.")

    def update_card(self, card_update: Union[Dict, schemas.NodeUpdate]):
        """
        Updates a card.

        Change one or multiple properties of a card in the board.
        The card is identified by its id in the card_update.
        The type of a card cannot the changed.

        Parameters
        ----------
        card_update (Union[Dict, schemas.NodeUpdate]):
            The card update. Can be either a dict with "id" and the properties
            to update or a NodeUpdate.

        Returns
        -------

        Raises
        ------
        ValidationError
            If the card_update is invalid
        BoardUpdateError
            If the card_update is illegal

        Examples
        --------
        >>> board = Board()
        >>> board.add_card({'id': 'befafcef-5f31-471d-97fd-a129844b66c3',
        >>>                 'type': 'note', 'position': {'x': 500, 'y': 500}})
        >>> board.cards[0].position
        Position(x=500, y=500)
        >>> board.update_card({'id': 'befafcef-5f31-471d-97fd-a129844b66c3',
        >>>                    'position': {'x': -100}})
        >>> board.cards[0].position
        Position(x=-100, y=500)
        """
        if not isinstance(card_update, schemas.NodeUpdate):
            if "type" not in card_update:
                card_update["type"] = self.get_card_by_id(card_update["id"]).type
            card_update = schemas.NodeUpdate.validate(card_update)

        previous_card = self.get_card_by_id(card_update.id)
        if card_update.type != previous_card.type:
            raise BoardUpdateError(f"Cannot change card type from {previous_card.type} to {card_update.type}")

        previous_card_dict = previous_card.dict()
        card_update_dict = card_update.dict(exclude_none=True)

        updated_dict = deep_update(previous_card_dict, card_update_dict)
        updated_card = schemas.Node.validate(updated_dict)

        index = self._board.nodes.index(previous_card)
        self._board.nodes[index] = updated_card

    @staticmethod
    def create_card(type: str,
                    id: str = None,
                    position: Dict[str, int] = None,
                    size: Dict[str, int] = None,
                    type_specific: Dict[str, Any] = None):
        """
        Creates a card.

        Parameters
        ----------
        type (str): the type of the card.
        id (str): the id of the card. Will be automatically created if None.
        position (Dict[str, int]): the position, e.g. {"x": 100, "y": -100}
        size (Dict[str, int]): the size, e.g. {"width": 300, "height": 200}
        type_specific: the type_specific for the card type

        Returns
        -------
        schemas.Node: the card as a Node schema instance

        Raises
        ------
        ValidationError: If the arguments are incompatible with the Node schema
        """

        if id is None:
            id = str(uuid.uuid4())

        card = {"type": type, "id": id}
        if position is not None:
            card.update({"position": position})
        if size is not None:
            card.update({"size": size})
        if type_specific is not None:
            card.update({"type_specific": type_specific})

        return schemas.Node.validate(card)

    def add_connection(self, connection: Union[dict, schemas.Edge]):
        """
        Adds a connection to the board

        Parameters
        ----------
        connection (Union[Dict[str, Any], schemas.Edge]): The connection to add.

        Returns
        -------

        Raises
        ------
        DuplicateIdError: If the id of the connection is already in use.
        BoardConnectionError: If connection source or target could not be found
            or if the connection violates the connection rules.
        """
        if not isinstance(connection, schemas.Edge):
            connection = schemas.Edge.validate(connection)

        if connection.id in self.connection_ids:
            raise DuplicateIdError("Duplicate node id detected.")
        if connection.connections.source.id not in self.card_ids:
            raise IdNotFoundError("Connection source card not found.")
        if connection.connections.target.id not in self.card_ids:
            raise IdNotFoundError("Connection target card not found.")

        self.check_connection_rules(connection)

        self._board.edges.append(connection)

    def remove_connection(self, connection: Union[Dict, schemas.Edge]):
        """
        Removes a connection.

        Parameters
        ----------
        connection (Union[Dict, schemas.Edge]):
            The connection to delete or a dict with {"id": connection_id}

        Returns
        -------

        Raises
        ------
        IdNotFoundError: If the id of the connection could not be found.
        """
        if not isinstance(connection, schemas.id_schema.EdgeId):
            connection = schemas.id_schema.EdgeId.validate(connection)
        connection_id = connection.id

        for index in range(len(self.connections)-1, -1, -1):
            if self.connections[index].id == connection_id:
                self.connections.pop(index)
                return None
        raise IdNotFoundError("Connection not found.")

    def update_connection(self, connection_update: Union[Dict, schemas.EdgeUpdate]):
        """
        Updates a connection.

        Change one or multiple properties of a connection in the board.
        The connection is identified by its id in the connection_update.
        The type of a connection as well as its source and target cannot the changed.

        Parameters
        ----------
        connection_update (Union[Dict, schemas.EdgeUpdate]):
            The connection update. Can be either a dict with "id" and the properties
            to update or a EdgeUpdate.

        Returns
        -------

        Raises
        ------
        ValidationError
            If the connection_update is invalid
        BoardUpdateError
            If the connection_update is illegal
        """
        if not isinstance(connection_update, schemas.EdgeUpdate):
            if "type" not in connection_update:
                connection_update["type"] = self.get_connection_by_id(
                    connection_update["id"]).type
            connection_update = schemas.EdgeUpdate.validate(connection_update)

        previous_connection = self.get_connection_by_id(connection_update.id)
        if connection_update.type != previous_connection.type:
            raise BoardUpdateError(f"Cannot change connection type from "
                                   f"{previous_connection.type} to {connection_update.type}")

        previous_connection_dict = previous_connection.dict()
        connection_update_dict = connection_update.dict(exclude_none=True)

        updated_dict = deep_update(previous_connection_dict, connection_update_dict)
        updated_connection = schemas.Edge.validate(updated_dict)

        if updated_connection.connections != previous_connection.connections:
            raise BoardUpdateError(f"Cannot change connection source or target.")

        index = self._board.edges.index(previous_connection)
        self._board.edges[index] = updated_connection

    def _remove_all_connections_to_card_id(self, card_id):
        # get all connections
        connections = self.get_all_connections_of_card(card_id)

        for conn in connections:
            self.remove_connection(conn)

    @staticmethod
    def create_connection(type: str,
                          connections: Dict[str, Dict],
                          id: str = None,
                          type_specific: dict = None):
        """
        Creates a connection

        Parameters
        ----------
        type (str): the type of the connection
        connections (Dict[str, Dict]): the connections, {"source": {"id": ..., "connector: ...}, "target": {...}}
        id (str): the uuid4 of the connection
        type_specific (dict): the type specifics of the connection type.

        Returns
        -------
        schemas.Edge: the connection as an Edge instance
        """

        if id is None:
            id = str(uuid.uuid4())

        connection = {"type": type, "id": id, "connections": connections}
        if type_specific is not None:
            connection.update({"type_specific": type_specific})

        return schemas.Edge.validate(connection)

    def add_path_element(self, element: Union[dict, schemas.PathElement],
                         index: int = None):
        """
        Adds an element to the board's path

        Parameters
        ----------
        element (Union[Dict[str, Any], schemas.PathElement]): The element to add.
        index (int): The position of the element.

        Returns
        -------

        Raises
        ------
        DuplicateIdError: If the id of the element is already in use.
        """
        if not isinstance(element, schemas.PathElement):
            element = schemas.PathElement.validate(element)

        if element.id in self.path_element_ids:
            raise DuplicateIdError("Duplicate element id detected.")

        self.check_path_link_rules(element)

        if index is None:
            index = len(self.path.linearTasks)
        self.path.linearTasks.insert(index, element)

    def remove_path_element(self, element: Union[Dict, schemas.PathElement]):
        """
        Removes a path element.

        Parameters
        ----------
        element (Union[Dict, schemas.PathElement]):
            The element to remove or a dict with {"id": element_id}

        Returns
        -------

        Raises
        ------
        IdNotFoundError: If the id of the card could not be found.
        """
        if not isinstance(element, schemas.id_schema.ElementId):
            element = schemas.id_schema.ElementId.validate(element)
        element_id = element.id

        for index in range(len(self.path_elements)-1, -1, -1):
            if self.path_elements[index].id == element_id:
                self.path_elements.pop(index)
                return None
        raise IdNotFoundError("Path Element not found.")

    def move_path_element(self, element: Union[Dict, schemas.PathElement], index: int):
        """
        Moves a path element to a new index.

        Parameters
        ----------
        element (Union[Dict, schemas.PathElement]):
            The element to move or a dict with {"id": element_id}
        index (int):
            The new index of the element

        Returns
        -------

        Raises
        ------
        IdNotFoundError: If the id of the card could not be found.
        """
        if not isinstance(element, schemas.id_schema.ElementId):
            element = schemas.id_schema.ElementId.validate(element)
        element_id = element.id

        element = self.get_path_element_by_id(element_id)
        self.path_elements.remove(element)
        self.path_elements.insert(index, element)

    def update_path_element(self, element_update: Union[Dict, schemas.PathElementUpdate]):
        """
        Updates a path element.

        Change one or multiple properties of an element in the board's path.
        The element is identified by its id in the element_update.
        The type of an element cannot the changed.

        Parameters
        ----------
        element_update (Union[Dict, schemas.PathElementUpdate]):
            The element update. Can be either a dict with "id" and the properties
            to update or a PathElementUpdate.

        Returns
        -------

        Raises
        ------
        ValidationError
            If the element_update is invalid
        BoardUpdateError
            If the element_update is illegal
        """
        if not isinstance(element_update, schemas.PathElementUpdate):
            if "type" not in element_update:
                element_update["type"] = self.get_path_element_by_id(element_update["id"]).type
            element_update = schemas.PathElementUpdate.validate(element_update)

        previous_element = self.get_path_element_by_id(element_update.id)
        if element_update.type != element_update.type:
            raise BoardUpdateError(f"Cannot change element type from {previous_element.type} to {element_update.type}")

        previous_element_dict = previous_element.dict()
        element_update_dict = element_update.dict(exclude_none=True)

        updated_dict = deep_update(previous_element_dict, element_update_dict)
        updated_element = schemas.PathElement.validate(updated_dict)

        self.check_path_link_rules(updated_element)

        index = self.path_elements.index(previous_element)
        self.path_elements[index] = updated_element

    @staticmethod
    def create_path_element(type: str,
                            id: str = None,
                            type_specific: dict = None):
        """
        Creates a path element

        Parameters
        ----------
        type (str): the type of element
        id (str): the uuid4 of the element
        type_specific (dict): the type specifics of the element type.

        Returns
        -------
        schemas.PathElement: the path element as an PathElement instance
        """

        if id is None:
            id = str(uuid.uuid4())

        element = {"type": type, "id": id}
        if type_specific is not None:
            element.update({"type_specific": type_specific})

        return schemas.PathElement.validate(element)

    def check_connection_rules(self, edge: schemas.Edge):
        """Validates whether `edge` can be added to board.
        Checks whether the connection rules are fulfilled.

        Parameters
        ----------
        edge : schemas.Edge

        Raises
        -------
        BoardConnectionError: If the connection violates the connection rules.

        """

        # 0. get connection type
        conn_type = edge.type

        # check that connection is not a loop
        if edge.connections.source == edge.connections.target:
            raise BoardConnectionError("Target and source connector must not be the same.")

        for source_target in ("source", "target"):

            # 1. fetch node properties
            node_id = getattr(edge.connections, source_target).id
            node_connector = getattr(edge.connections, source_target).connector

            # 2. check if node type has that connector
            node_type = self.get_card_by_id(node_id).type
            if (connection_rules.CONNECTORS[node_connector]
                    not in connection_rules.NODE_CONNECTORS[node_type]):
                raise BoardConnectionError(f"{source_target} card of type {node_type} does not"
                                           f" have a connector of type {node_connector}.")

            # 3. check if connector supports the connection type
            connection_specs = (
                connection_rules.CONNECTORS[node_connector].source_to if source_target == "source"
                else connection_rules.CONNECTORS[node_connector].target_to)

            edge_spec = None
            for temp_edge_spec in connection_specs:
                if temp_edge_spec["type"] == conn_type:
                    edge_spec = temp_edge_spec
                    break
            if not edge_spec:
                raise BoardConnectionError(f"{source_target} card connector {node_connector} does not "
                                           f"support a connection of type {conn_type}.")

            # 4. if connector supports only a finite amount of connection type check that
            if edge_spec["amount"] != -1:  # -1 stands for infinite
                all_conns = self.get_all_connections_of_card(node_id, connector=node_connector)
                all_conns = [c for c in all_conns
                             if (c.type == conn_type) and
                             c.id != edge.id and
                             (getattr(c.connections, source_target).id == node_id)]
                if len(all_conns) >= edge_spec["amount"]:
                    raise BoardConnectionError(f"{source_target} card connector {node_connector} already "
                                               f"has maximum amount of connections of type {conn_type}.")

    def check_path_link_rules(self, element: schemas.PathElement):
        if element.type == "note":
            if card_id := element.type_specific.linkedNodeId:
                if self.get_card_by_id(card_id).type != "note":
                    raise PathLinkError("Note type elements must be linked to note type cards.")
                for e in self.path_elements:
                    if e.type == "note":
                        if e.id != element.id and e.type_specific.linkedNodeId == card_id:
                            raise PathLinkError(f"Path element {e.id} is already linked to card {card_id}.")
        if element.type == "bot":
            if card_id := element.type_specific.linkedNodeId:
                if self.get_card_by_id(card_id).type != "bot":
                    raise PathLinkError("Bot type elements must be linked to bot type cards.")
                for e in self.path_elements:
                    if e.type == "bot":
                        if e.id != element.id and e.type_specific.linkedNodeId == card_id:
                            raise PathLinkError(f"Path element {e.id} is already linked to card {card_id}.")
        if element.type == "action-chain":
            for action in element.type_specific.actions:
                if self.get_card_by_id(action.nodeId).type != "bot":
                    raise PathLinkError("Actions must refer to bot type cards.")

    def get_partial_board(self, contained_card_ids: List[str]) -> 'Board':
        """
        Returns a Board instance that only contains the cards specified
        in `contained_card_ids` as well as the connections that
        fully contained within these cards.

        Parameters
        ----------
        contained_card_ids : List[str]
            The list of card ids that make up the partial board.

        Returns
        -------
        Board

        """
        partial_board = Board()

        for card in self.cards:
            if card.id in contained_card_ids:
                partial_board.add_card(card.copy())

        for connection in self.connections:
            if (connection.connections.source.id in contained_card_ids and
                    connection.connections.target.id in contained_card_ids):
                partial_board.add_connection(connection.copy())

        return partial_board

