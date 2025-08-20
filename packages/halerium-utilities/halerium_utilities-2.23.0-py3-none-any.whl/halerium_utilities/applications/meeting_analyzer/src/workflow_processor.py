# Workflow Processor
# This class processes the generated transcript by executing the worklow in order.
# It can differentiate between preprocessing (blue and yellow frames) and postprocessing (red frames) cards.
# Red frames are executed only after the user has reviewed and approved the transcript.

from enum import Enum
from halerium_utilities.board import BoardNavigator
from halerium_utilities.collab import CollabBoard
from halerium_utilities.prompt.agents import call_agent
import json
import logging
from pathlib import Path
import requests

# setup logging with debug level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class WorkflowProcessorMode(Enum):
    """
    Enum class for the workflow mode.
    """

    PREPROCESS = 0
    POSTPROCESS = 1


class WorkflowProcessor:
    """
    Class for processing a transcript according to the provided workflow.
    """

    def __init__(self, board_path: str, session_id: str) -> None:
        self.session_id = session_id
        self.board_path = Path(board_path)
        self.collab_board = CollabBoard(self.board_path, pull_on_init=True)
        self.navigator = BoardNavigator(self.collab_board)
        self.execution_order = self.navigator.get_execution_order(
            self.navigator.cards, keep_only_executable=True
        )

        # separate the cards into preprocessing, result and postprocessing cards
        self.preprocessing_cards = [
            card_id
            for card_id in self.execution_order
            if self._is_preprocess_card(card_id)
        ]

        self.result_cards = [
            card_id for card_id in self.execution_order if self._is_result_card(card_id)
        ]

        self.postprocessing_cards = [
            card_id
            for card_id in self.execution_order
            if self._is_postprocess_card(card_id)
        ]

        logger.debug(
            f"Preprocessing cards: {self.preprocessing_cards}\nResult cards: {self.result_cards}\nPostprocessing cards: {self.postprocessing_cards}"
        )

        print(f"Preprocessing cards: {self.preprocessing_cards}")
        print(f"Result cards: {self.result_cards}")
        print(f"Postprocessing cards: {self.postprocessing_cards}")

    def execute(
        self, mode: WorkflowProcessorMode = WorkflowProcessorMode.PREPROCESS
    ) -> tuple[dict, dict]:
        """
        Processes the transcript by executing cards in blue and yellow frames.
        Does not execute cards in red frames.

        Args:
            mode (WorkflowProcessorMode, optional): Mode of the processor. Defaults to WorkflowProcessorMode.PREPROCESS.

        Returns:
            tuple[dict, dict]: Dictionary of card IDs and their outputs, dictionary of card IDs and their errors.
        """
        cards = (
            self.preprocessing_cards + self.result_cards
            if mode == WorkflowProcessorMode.PREPROCESS
            else self.postprocessing_cards
        )
        ids_and_answers = {}
        ids_and_errors = {}
        for card_id in cards:
            answer = self._execute_botcard(card_id)

            # only store the output of the result cards, the rest are not displayed
            if card_id in self.result_cards:
                ids_and_answers[card_id] = answer

            if "error" in answer.lower():
                ids_and_errors[card_id] = answer

        return ids_and_answers, ids_and_errors

    def _execute_botcard(self, card_id: str) -> str:
        """
        Execute a botcard and update the board with the output.

        Args:
            board (Board): Halerium board object.
            card_id (str): ID of the botcard to execute.

        Returns:
            str: Output of the botcard.
        """
        # pull the board to get the latest data
        self.collab_board.pull()

        # update navigator with the latest data
        self.navigator = BoardNavigator(self.collab_board)

        # get card bot type to determine how to execute it
        card_type = self.navigator.get_bot_type(card_id)
        logger.debug(f"Executing card {card_id} of type {card_type}.")

        result = ""
        if card_type != "jupyter-kernel":
            print(f"Calling agent for card {card_id}")
            gen = call_agent(self.collab_board.to_dict(), card_id, parse_data=True)
            for data in gen:
                if data.event == "chunk":
                    result += data.data["chunk"]

        else:
            print(f"Running code of card {card_id}")
            is_last_card = self.navigator.get_bot_successor_card_ids(card_id) == []
            path = self.board_path.resolve().relative_to(Path.home())

            # inject __halerium_card into code
            __halerium_card = {
                "id": card_id,
                "path": str(path),  # string, because PosixPath is not serializable
                "setup_id": self.navigator.get_setup_card_id(card_id),
            }

            code = (
                f"__halerium_card = {__halerium_card}\n"
                + self.navigator.cards[card_id].type_specific.prompt_input
            )

            payload = {
                "__halerium_card": __halerium_card,
                "code": code,
            }

            execute_url = "http://0.0.0.0:8800/execute_kernel_code"
            process_result = requests.post(
                url=execute_url,
                json=payload,
            )
            result = json.dumps(process_result.json())

            print(f"Result for {card_id}: {result}")

            # only cleanup if it is the last card in the chain, otherwise we lose state
            if is_last_card:
                cleanup_url = "http://0.0.0.0:8800/cleanup"
                cleanup_result = requests.post(
                    url=cleanup_url,
                    json={
                        "setup_id": self.navigator.get_setup_card_id(card_id),
                        "path": f"{self.session_id}_{path.name}",
                    },
                )
                if cleanup_result.ok:
                    print(f"{self.session_id}: Kernel cleanup successful")
                else:
                    print(f"Kernel cleanup failed: {cleanup_result.text}")

        # update the board with the output
        print(f"Updating card {card_id}")
        self.collab_board.update_card(
            {"id": card_id, "type_specific": {"prompt_output": result}}
        )

        self.collab_board.push()

        return result

    def _is_color(self, card_id: str, color_name: str) -> bool:
        """
        Check if a card is in a frame of a certain color.

        Args:
            card_id (str): Card ID.
            color_name (str): Name of the color.

        Raises:
            ValueError: If the card is contained in multiple frames.

        Returns:
            bool: True if the card is in a frame of the specified color, False otherwise.
        """
        if not color_name:
            return False

        containing_frame = self.navigator.get_containing_frame_ids(card_id)

        # cards can only be in one frame
        if len(containing_frame) > 1:
            logger.error(
                f"Card {card_id} is contained in multiple frames: {containing_frame}"
            )
            raise ValueError(
                f"Card {card_id} is contained in multiple frames: {containing_frame}"
            )

        for frame_id in containing_frame:
            frame_color = getattr(
                self.navigator.cards[frame_id].type_specific, "color", None
            )
            if frame_color == color_name:
                return True

        return False

    def _get_color_code(self, color: str) -> str | None:
        """
        Get the color code for a given color.

        Args:
            color (str): Color name.

        Returns:
            str | None: Color code.
        """
        colors = {
            "blue": "note-color-4",  # _is_preprocess_card
            "red": "note-color-6",  # _is_postprocess_card
            "yellow": "note-color-8",  # _is_result_card
        }

        if not color in colors:
            logger.error(f"Color {color} is not supported.")
            return None

        return colors.get(color)

    def _is_result_card(self, card_id: str) -> bool:
        return self._is_color(card_id, self._get_color_code("yellow"))

    def _is_preprocess_card(self, card_id: str) -> bool:
        return self._is_color(card_id, self._get_color_code("blue"))

    def _is_postprocess_card(self, card_id: str) -> bool:
        return self._is_color(card_id, self._get_color_code("red"))
