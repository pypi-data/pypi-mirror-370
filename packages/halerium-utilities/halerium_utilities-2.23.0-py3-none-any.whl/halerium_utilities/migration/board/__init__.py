from typing import Tuple

from .migrate_none_to_1_0 import migrate_board as v0_to_v1
from .migrate_1_1_to_1_2 import migrate_board as v1_1_to_v1_2
from .migrate_1_2_to_2_0 import migrate_board as v1_2_to_v2_0
from .migrate_2_0_to_2_1 import migrate_board as v2_0_to_v2_1
from .migrate_2_3_to_v2_4 import migrate_board as v2_3_to_v2_4
from .minor_migration import get_minor_migration


MIGRATION_SCRIPTS = {
    None: v0_to_v1,
    "1.0": get_minor_migration("1.1"),
    "1.1": v1_1_to_v1_2,
    "1.2": v1_2_to_v2_0,
    "2.0": v2_0_to_v2_1,
    "2.1": get_minor_migration("2.2"),
    "2.2": get_minor_migration("2.3"),
    "2.3": v2_3_to_v2_4,
    # add here new migrations, e.g.:
    # "1.0": v1_to_v2,
}


def migrate_newest(board_dict: dict) -> Tuple[bool, dict]:
    """
    Migrates the board to the most recent version.

    Parameters
    ----------
    board_dict: The board to migrate as dict.

    Returns
    -------
    A tuple of boolean (did any migration happen) and the migrated board as dict.

    """
    migrated = False
    while True:
        version = board_dict.get("version")
        migration = MIGRATION_SCRIPTS.get(version)
        if migration is None:
            break
        board_dict = migration(board_dict)
        migrated = True

    return migrated, board_dict
