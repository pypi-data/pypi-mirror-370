# halerium utilities
from halerium_utilities.board import Board

# infrastructure
from datetime import datetime
import os
from pathlib import Path


def create_meeting_board(
    transcript: str,
    meeting_template: Path = Path("./template.board"),
    meetings_path: Path = Path("./meetings"),
):

    # ensure Path type
    meetings_path = Path(meetings_path)
    meeting_template = Path(meeting_template)

    # create directories if they do not exist
    meetings_path.mkdir(exist_ok=True, parents=True)

    board = Board.from_json(meeting_template)

    # get all notes in the board that are of type "note" and have the title "Transcript"
    transcript_notes = [
        n
        for n in board.cards
        if n.type == "note" and n.type_specific.title.strip().lower() == "transcript"
    ]

    # set the message of the transcript notes to the transcript
    for note in transcript_notes:
        note.type_specific.message = transcript

    # create a new board
    meeting_board_path = meetings_path / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.board"
    board.to_json(meeting_board_path)

    return meeting_board_path


def get_meeting_board_deep_link(board_path: Path):

    base_url = os.getenv("HALERIUM_BASE_URL", "")
    tenant_key = os.getenv("HALERIUM_TENANT_KEY", "")
    project_id = os.getenv("HALERIUM_PROJECT_ID", "")
    board_path = os.path.abspath(board_path).replace("/home/jovyan/", "")

    deep_link = ""
    if base_url and tenant_key and project_id:
        deep_link = f"{base_url}/{tenant_key}/{project_id}/contents/{board_path}"

    return deep_link
