import logging


COLLAPSED_HEIGHT = 34


def migrate_node(node_dict):
    new_node = {
        "id": node_dict["id"],
        "position": node_dict["position"],
        "size": node_dict["size"],
        "type_specific": {}
    }

    processing_dict = {
        "note": process_note,
        "prompt-note": process_bot,
        "assistant-setup-note": process_setup,
        "vectorstore-note": process_vector_store_file
    }

    processing_dict[node_dict["type"]](
        new_node=new_node, node_dict=node_dict)

    return new_node


def process_note(new_node, node_dict):
    new_node["type"] = "note"

    new_node["type_specific"] = {
        "title": node_dict["title"],
        "message": node_dict["type_specific"]["message"],
        "color": node_dict["color"],
        "auto_size": node_dict["type_specific"].get("auto_size", False),
        "attachments": node_dict.get("attachments", {}),
    }

    if node_dict.get("collapsed", False):
        new_node["size"]["height"] = COLLAPSED_HEIGHT


def process_bot(new_node, node_dict):
    new_node["type"] = "bot"

    new_node["type_specific"] = {
        "prompt_input": node_dict["type_specific"]["prompt_input"],
        "prompt_output": node_dict["type_specific"]["prompt_output"],
        "auto_size": node_dict["type_specific"].get("auto_size", False),
        "split_size": node_dict["type_specific"].get("split_size", [16.73, 83.27]),
        "state": node_dict["type_specific"].get("state", "success"),
        "attachments": node_dict.get("attachments", {}),
    }

    if len(new_node["type_specific"]["split_size"]) != 2:
        new_node["type_specific"]["split_size"] = [16.73, 83.27]


def process_setup(new_node, node_dict):
    new_node["type"] = "setup"

    if node_dict["type_specific"]["assistant_type"] in ("dall-e", "stable-diffusion"):
        resolution = node_dict["type_specific"]["system_setup"].strip()
        if resolution not in ("1024x1024", "512x512"):
            resolution = "1024x1024"
        setup_args = {"resolution": resolution}
    elif node_dict["type_specific"]["assistant_type"] == "jupyter-kernel":
        setup_args = {}
    else:
        setup_args = {"system_setup": node_dict["type_specific"]["system_setup"]}

    new_node["type_specific"] = {
        "bot_type": node_dict["type_specific"]["assistant_type"],
        "setup_args": setup_args,
        "auto_size": node_dict["type_specific"].get("auto_size", False),
    }


def process_vector_store_file(new_node, node_dict):
    new_node["type"] = "vector-store-file"

    new_node["type_specific"] = {
        "title": node_dict["title"],
        "vector_store_file": node_dict["type_specific"]["vector_store_file"],
        "vector_store_file_type": node_dict["type_specific"]["vector_store_file_type"],
        "state": node_dict["type_specific"].get("state", "queued"),
    }


def migrate_edge(edge, old_board):

    type_dict = {
        "solid_line": "prompt_line",
        "solid_arrow": "solid_arrow",
        "dashed_arrow": "dashed_line",
    }

    new_edge = {
        "id": edge["id"],
        "type": type_dict[edge["type"]],
        "type_specific": {},
        "connections": {
            "source": {"id": edge["node_connections"][0], "connector": None},
            "target": {"id": edge["node_connections"][1], "connector": None},
        }
    }

    # find nodes
    source_node = None
    target_node = None
    for node in old_board["nodes"]:
        if node["id"] == edge["node_connections"][0]:
            source_node = node
        if node["id"] == edge["node_connections"][1]:
            target_node = node

    source_connector = None
    for e in source_node["edge_connections"]:
        if e["id"] == edge["id"]:
            source_connector = e["connector"]
    if source_node["type"] == "vectorstore-note":
        source_connector = "prompt-context-output"

    target_connector = None
    for e in target_node["edge_connections"]:
        if e["id"] == edge["id"]:
            target_connector = e["connector"]

    connector_dict = {
        "top": "note-top",
        "bottom": "note-bottom",
        "left": "note-left",
        "right": "note-right",
        "prompt-input": "prompt-input",
        "prompt-output": "prompt-output",
        "context-input": "context-input",
        "prompt-context-output": "context-output",
    }

    new_edge["connections"]["source"]["connector"] = connector_dict[source_connector]
    new_edge["connections"]["target"]["connector"] = connector_dict[target_connector]

    # special case: if dashed connections go from top to bottom instead of bottom to top repair this.
    if new_edge["type"] == "dashed_line":
        if (new_edge["connections"]["source"]["connector"] == "note-top" and
                new_edge["connections"]["target"]["connector"] == "note-bottom"):
            source = new_edge["connections"]["target"]
            target = new_edge["connections"]["source"]
            new_edge["connections"]["source"] = source
            new_edge["connections"]["target"] = target

    return new_edge


def migrate_board(board_dict):

    # 1. check version before starting migration
    if board_dict.get("version", None) is not None:
        raise Exception("Input board has wrong version.")

    new_board = {
        "version": "1.0",
        "nodes": [],
        "edges": [],
    }

    try:
        for old_node in board_dict["nodes"]:
            try:
                new_board["nodes"].append(migrate_node(old_node))
            except Exception as exc:
                logging.warning(f"could not migrate node {exc}")
    except Exception:
        raise Exception("Input board does not contain valid nodes.")

    try:
        for old_edge in board_dict["edges"]:
            try:
                new_board["edges"].append(migrate_edge(old_edge, board_dict))
            except Exception as exc:
                logging.warning(f"could not migrate edge {exc}")
    except Exception:
        raise Exception("Input board does not contain valid edges.")

    return new_board
