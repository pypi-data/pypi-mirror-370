from copy import deepcopy


def migrate_board(board_dict):

    # 1. check version before starting migration
    if board_dict.get("version", None) != "1.2":
        raise Exception("Input board has wrong version.")

    migrated_board = deepcopy(board_dict)
    migrated_board["version"] = "2.0"

    # 1. Add workflows property
    if "workflows" not in migrated_board:
        migrated_board["workflows"] = []
    return migrated_board
