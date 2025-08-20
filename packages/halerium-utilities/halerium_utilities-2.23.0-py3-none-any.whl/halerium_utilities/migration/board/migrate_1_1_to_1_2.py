from copy import deepcopy


def migrate_board(board_dict):

    # 1. check version before starting migration
    if board_dict.get("version", None) != "1.1":
        raise Exception("Input board has wrong version.")

    migrated_board = deepcopy(board_dict)
    migrated_board["version"] = "1.2"

    # 1. collect all frames
    frame_ids = []
    for node in migrated_board["nodes"]:
        if node["type"] == "frame":
            frame_ids.append(node["id"])

    # 2. go through edges and replace frame context-output with note-bottom
    for edge in migrated_board["edges"]:
        # 2.1 check whether edge source node is a frame
        if edge["connections"]["source"]["id"] in frame_ids:
            # 2.2 check whether edge source connector is "context-output"
            if edge["connections"]["source"]["connector"] == "context-output":
                # 2.3 replace context-output with note-bottom
                edge["connections"]["source"]["connector"] = "frame-bottom"

    return migrated_board
