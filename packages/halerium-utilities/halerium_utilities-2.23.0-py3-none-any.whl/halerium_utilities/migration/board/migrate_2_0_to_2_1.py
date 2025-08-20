import logging
from copy import deepcopy
from halerium_utilities.board.schemas import Node

def migrate_board(board_dict):

    # 1. check version before starting migration
    if board_dict.get("version", None) != "2.0":
        raise Exception("Input board has wrong version.")

    migrated_board = deepcopy(board_dict)
    migrated_board["version"] = "2.1"

    # 1. Change store_uuids of setup_args from array to dictionary
    for node in [node for node in migrated_board["nodes"]
                 if node["type"] == "setup" and
                 node["type_specific"]["setup_args"].get("store_uuids", None)]:
        new_store_uuids = {}
        store_uuids =node["type_specific"]["setup_args"]["store_uuids"]

        for uuid in store_uuids:
            new_store_uuids[uuid] = ["read", "write"]

        node["type_specific"]["setup_args"]["store_uuids"] = new_store_uuids

    # 2. migrate vector-store cards
    for index, node in enumerate(migrated_board["nodes"]):
        if node["type"] == "vector-store-file":
            file_path = node["type_specific"]["vector_store_file"]
            file_type = node["type_specific"]["vector_store_file_type"]
            new_type_specific = {
                "title": "deprecated vector-store-card",
                "message": f"path: {file_path}\ntype: {file_type}",
                "color": "note-color-1",
                "auto_size": False,
                "attachments": {}
            }

            node["type"] = "note"
            node["type_specific"] = new_type_specific

            node_id = node["id"]
            # update connections
            for edge in migrated_board["edges"]:
                if edge["connections"]["source"]["id"] == node_id:
                    edge["connections"]["source"]["connector"] = "note-bottom"

    return migrated_board
