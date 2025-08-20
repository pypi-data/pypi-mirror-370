from copy import deepcopy


def migrate_board(board_dict):

    # 1. check version before starting migration
    if board_dict.get("version", None) != "2.3":
        raise Exception("Input board has wrong version.")

    migrated_board = deepcopy(board_dict)
    migrated_board["version"] = "2.4"

    for workflow in migrated_board["workflows"]:
        for element in workflow["linearTasks"]:
            if element["type"] == "upload":
                if not isinstance(element["type_specific"]["chunkingArguments"], list):
                    element["type_specific"]["chunkingArguments"] = []

    return migrated_board
