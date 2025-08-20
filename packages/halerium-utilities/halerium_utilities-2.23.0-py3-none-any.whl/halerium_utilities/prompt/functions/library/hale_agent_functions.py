import json

from datetime import datetime
from pathlib import Path

from halerium_utilities.hal_es import HalE, BoardPathSession, get_workspace_hales_async
from halerium_utilities.board import Board


async def find_hale_agents():
    data = await get_workspace_hales_async()
    subagent_hales = []
    for hale in data:
        try:
            get_agent_specification(hale.name)
            subagent_hales.append({"agent_name": hale.name, "status": "Valid agent"})
        except ValueError as exc:
            subagent_hales.append({"agent_name": hale.name, "status": f"Invalid agent: {exc}"})

    return subagent_hales


def _simplify_note(note):
    return {
        "title": getattr(note.type_specific, "title", ""),
        "message": getattr(note.type_specific, "message", "")
    }


subagent_description_text = """
Subagents must follow the structure:
 1. 0-N note elements with distinct titles for inputs
 2. ONE action-chain element
 3. 0-M note elements with distinct titles for outputs
"""


def get_agent_specification(agent_name):
    new_hale = HalE.from_name(agent_name)
    board_path = new_hale.template_board
    full_session_path = Path.home() / board_path.lstrip("/")
    board = Board.from_json(full_session_path)
    path_elements = [board.resolve_path_element(e) for e in board.path_elements]

    action_indices = [
        i for i, e in enumerate(path_elements) if e.type == 'action-chain'
    ]
    if not action_indices:
        raise ValueError("No action-chain element found." + subagent_description_text)
    if len(action_indices) > 1:
        raise ValueError("Multiple action-chain elements found." + subagent_description_text)

    if any(e.type not in ("note", "action-chain") for e in path_elements):
        raise ValueError("Found unsupported elements." + subagent_description_text)

    action_index = action_indices[0]
    action_element = path_elements[action_index]
    action_title = getattr(action_element.type_specific, "title", "")

    notes_before = [
        _simplify_note(e) for i, e in enumerate(path_elements)
        if e.type == 'note' and i < action_index
    ]
    notes_after = [
        _simplify_note(e) for i, e in enumerate(path_elements)
        if e.type == 'note' and i > action_index
    ]

    return {
        "agent_name": agent_name,
        "inputs": notes_before,
        "action": action_title,
        "outputs": notes_after
    }


async def execute_agent(agent_name, input_elements, __halerium_card):
    input_elements = json.loads(input_elements)

    parent_board_path = Path.home() / __halerium_card.get("path").lstrip("/")
    agent_runs_folder = parent_board_path.parent

    agent_board_path = agent_runs_folder / f"{agent_name} {datetime.now().isoformat()}.board"
    hale_instance = BoardPathSession.from_hale_name(agent_name, target_path=agent_board_path)
    path_elements = await hale_instance.get_elements_async()

    for input_note in input_elements:
        title = input_note["title"]
        message = input_note["message"]

        matching_note = next(
            (e for e in path_elements if e.type == 'note' and hasattr(e.type_specific, 'title')
             and e.type_specific.title == title),
            None
        )
        if not matching_note:
            raise ValueError(f"No note element found with title '{title}'.")
        
        await hale_instance.insert_text_async(element_id=matching_note.id, text=message, field="message")

    action_chain_element = next((e for e in path_elements if e.type == 'action-chain'), None)
    if not action_chain_element:
        raise ValueError("No action-chain element found.")
    
    action_index = path_elements.index(action_chain_element)
    await hale_instance.execute_actions_async(element_id=action_chain_element.id)
    updated_elements = await hale_instance.get_elements_async()

    notes_after_action = [
        simplified for i, e in enumerate(updated_elements)
        if i > action_index and e.type == "note" and (simplified := _simplify_note(e)) is not None
    ]

    return {
        "outputs": notes_after_action
    }
