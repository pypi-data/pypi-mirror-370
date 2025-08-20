from .chatbot_roles import ChatbotRoles
from enum import Enum
from halerium_utilities.board.board import Board
from halerium_utilities.board.schemas import Node
from halerium_utilities.board.navigator import BoardNavigator
from halerium_utilities.utils.switch_runner import switch_runner
import io
import json
import logging
from pathlib import Path
from typing import Any, Optional, Dict


class CardSettings(Enum):
    """
    Enum class for card settings.
    """

    WIDTH = 520
    HEIGHT = 320
    MARGIN = 20


class BoardManager:
    logger = logging.getLogger(__name__)

    @staticmethod
    def get_board(
        path: Path,
        as_dict: bool = False,
    ) -> Board | dict:
        """
        Returns the chatbot board either as Board or as dictionary.

        Args:
            path (Path): The absolute path to the board that should be used as template.
            as_dict (bool, optional): Returns the board as dict if true, else Board. Defaults to False.

        Returns:
            Board | dict: Board or dict object of the loaded Halerium board.
        """
        try:
            with open(path, "r") as f:
                board = Board.from_json(f)
                board = switch_runner(board)
        except FileNotFoundError:
            BoardManager.logger.error(f"Board file {path} not found.")
        else:
            BoardManager.logger.debug("loaded board file")
            return board if not as_dict else board.to_dict()

    @staticmethod
    def _new_conversation_card(message: str, current_card: Node) -> Node:
        """
        Creates a new bot card and sets the prompt_input to the given message.

        Args:
            message (str): The message that should be set as prompt_input.
            current_card (Node): The current bot card.

        Returns:
            Node: The new bot card.
        """
        current_card_pos = current_card.position

        new_card = Board.create_card(
            type="bot",
            size={
                "width": CardSettings.WIDTH.value,
                "height": CardSettings.HEIGHT.value,
            },
            position={
                "x": current_card_pos.x
                + CardSettings.WIDTH.value
                + CardSettings.MARGIN.value,
                "y": current_card_pos.y,
            },
            type_specific={
                "prompt_input": message,
                "prompt_output": "",
                "attachments": {},
            },
        )

        return new_card

    @staticmethod
    def update_board(
        board: dict,
        current_card_id: str,
        role: str,
        message: str,
        attachments: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> dict:
        with io.StringIO(json.dumps(board)) as board_io:
            board: Board = Board.from_json(board_io)

        current_card = board.get_card_by_id(current_card_id)

        # if role is user, add user_prompt a new card
        if role == ChatbotRoles.USER.value:
            new_card = BoardManager._new_conversation_card(message, current_card)

            BoardManager.logger.debug(f"Current card id: {current_card_id}")
            BoardManager.logger.debug(f"New card id: {new_card.id}")

            # add new card with connections
            board.add_card(new_card)
            edge = board.create_connection(
                type="prompt_line",
                connections={
                    "source": {"id": current_card.id, "connector": "prompt-output"},
                    "target": {"id": new_card.id, "connector": "prompt-input"},
                },
            )
            BoardManager.logger.debug(f"New edge: {edge}")

            board.add_connection(edge)

            BoardManager.logger.debug("Added new conversation card with user prompt.")
            return dict(board=board.to_dict(), new_card_id=new_card.id)

        elif role == ChatbotRoles.ASSISTANT.value:
            # if role is assistant, update prompt_output
            current_card.type_specific.prompt_output = message

            BoardManager.logger.debug(
                "Updated current conversation card with bot response."
            )

            # if there is an attachment, add it to the card
            if attachments is not None:
                current_card.type_specific.attachments.update(attachments)
                BoardManager.logger.debug("Added attachment(s) to card.")

            return {"board": board.to_dict(), "new_card_id": current_card.id}

        elif role == ChatbotRoles.SYSTEM.value:
            # if role is system, update the setup card's system message
            nav = BoardNavigator(board)
            setup_card_id = nav.get_setup_card_id(current_card_id)
            setup_card = board.get_card_by_id(setup_card_id)
            setup_card.type_specific.setup_args["system_setup"] += message

            BoardManager.logger.debug("Updated setup card's system message")
            return dict(board=board.to_dict(), new_card_id=current_card.id)

    @staticmethod
    def get_chain_parameters(path: Path | str, current_bot_card_id: str):
        """
        Extracts the bot type and system message from the setup card, as well as the initial user prompt and bot answer.
        """
        # get board as Board
        board = BoardManager.get_board(path)

        # create board navigator
        navigator = BoardNavigator(board)

        # get setup card id of the prompt chain
        setup_card_id = navigator.get_setup_card_id(current_bot_card_id)

        # get bot_type and system_message from setup card
        bot_type = navigator.get_bot_type(setup_card_id)
        setup_message = navigator.get_setup_args(setup_card_id).get("system_setup")

        # extract prompt in- and output
        initial_prompt_input = navigator.get_prompt_input(current_bot_card_id)
        initial_prompt_output = navigator.get_prompt_output(current_bot_card_id)

        # build parameter dictionary
        configuration = {
            "setup_card_id": setup_card_id,
            "setup_message": setup_message,
            "bot_type": bot_type,
            "current_bot_card_id": current_bot_card_id,
            "initial_prompt": initial_prompt_input,
            "initial_response": initial_prompt_output,
        }

        return configuration

    @staticmethod
    def export_as_json(board: dict, name: str = ""):
        """
        Exports the board as json.
        """
        try:
            with open(f"test{name}.board", "w") as f:
                json.dump(board, f)
        except Exception as e:
            BoardManager.logger.error(f"Error exporting board: {e}")
