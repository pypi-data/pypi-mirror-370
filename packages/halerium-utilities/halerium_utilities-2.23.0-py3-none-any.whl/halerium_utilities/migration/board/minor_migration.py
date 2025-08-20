from copy import deepcopy


def get_minor_migration(target_version):
    """
    Construct trivial migration function that just changes the version tag

    Parameters
    ----------
    target_version: str
        the target version

    Returns
    -------
    migration_function
    """
    def migrate_board(board_dict):
        migrated_board = deepcopy(board_dict)
        migrated_board["version"] = str(target_version)
        return migrated_board

    return migrate_board
