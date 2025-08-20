import os

from typing import Optional
from pydantic.v1 import BaseModel, Field


class BotArgument(BaseModel):
    board_path: str = Field(description="Path of the board file defining the subagent. Example: '/home/jovyan/folder/agent.board'")
    task: str = Field(description="The instructions for the bot. Will be inserted into the first chat card of the subagent.")


async def execute_subagent(data: BotArgument):
    """
    Executes an agent defined in a board and returns its final answer.
    The board_path should be provided as an absolute path including the .board file ending.
    """
    from datetime import datetime
    from pathlib import Path
    import asyncio
    from halerium_utilities.prompt.agents import call_agent_async
    from halerium_utilities.prompt.agents_cleanup import cleanup_board_async
    from halerium_utilities.board.navigator import BoardNavigator
    from halerium_utilities.board.board import Board

    board_path: str = data.get("board_path")
    board_path = Path(board_path)
    log_path = Path(board_path.parent) / "logs"

    task: str = data.get("task")

    if not board_path or not task:
        return "Please specify the subagents board_path and task!"

    try:
        log_path.mkdir(exist_ok=True, parents=True)
    except Exception as e:
        return f"failed to setup directories: {str(e)}"

    if not board_path.exists():
        return f"Board path does not exist: {board_path}."

    try:
        b = Board.from_json(board_path)

        run_filename = log_path / f"{datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}_{board_path.name}"
        if os.path.exists(run_filename):
            run_filename = log_path / f"{datetime.now().strftime('%Y-%m-%d_%H_%M_%S.%f')}_{board_path.name}"
        b.to_json(run_filename)

        function_path = str(run_filename.resolve().relative_to("/home/jovyan"))

        nav = BoardNavigator(b)

        # execute agent
        ex_ord = nav.get_execution_order(nav.cards)

        b.update_card({
            "id": ex_ord[0],
            "type_specific": {
                "prompt_input": task
            }
        })
        b.to_json(run_filename)

        for ex in ex_ord:
            res = ""
            attachments = {}
            async for e in call_agent_async(b.to_dict(), ex, path=function_path, parse_data=True):
                if e.event == 'chunk':
                    res += e.data.get('chunk', '')
                if e.event == "function":
                    try:
                        attachments[e.data["id"]] = {"function": e.data}
                    except KeyError:
                        pass
                if e.event == "function_output":
                    try:
                        attachments[e.data["id"]]["function"].update(e.data)
                    except KeyError:
                        pass

            card_update = {
                "id": ex,
                "type_specific": {
                    "prompt_output": res
                }
            }
            if attachments:
                old_attachments = b.get_card_by_id(ex).type_specific.attachments
                card_update["type_specific"]["attachments"] = {**old_attachments, **attachments}

            # Update the card with the agent response
            b.update_card(card_update)
            b.to_json(run_filename)

        await cleanup_board_async(b.to_dict(), path=function_path)

    except Exception as e:
        return str(e)

    return res


class GetAssistantsArgument(BaseModel):
    source_path: Optional[str] = Field(
        default=None,
        description="Relative or absolute path of the folder in which the subagent .board files are. Will default to `/home/jovyan/[Agents]/` if not specified."
    )


async def get_subagents(data: GetAssistantsArgument):
    """
    This function collects boards files defining subagents in either the 
    default [Agents] folder or in a user specified folder.
    It will return the subagents as a dict with the absolute board paths as keys.
    These subagents can then be executed with the `execute_subagent` function.
    """
    from pathlib import Path
    from halerium_utilities.board import Board
    import json

    default_source_path = Path("/home/jovyan/[Agents]/")
    s_path: str = data.get("source_path", None)
    source_path = Path(s_path).resolve() if s_path else default_source_path

    if not source_path.exists():
        if source_path == default_source_path:
            return "The default agents folder `[Agents]` does not exist in the home folder. Please create it or specify the source_path argument."
        else:
            return f"Source directory does not exist: {source_path}"

    assistants = {}

    for board_file in source_path.glob("*.board"):
        board = Board.from_json(board_file)

        table = [n for n in board.cards if n.type == "note"]
        description = None

        for note in table:
            if note.type_specific.title.lower().startswith("description"):
                description = note.type_specific.message
        assistants[str(board_file)] = {
            "description": description,
        }

    return json.dumps(assistants, indent=4)

