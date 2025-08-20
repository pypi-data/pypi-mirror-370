import uuid

from .api import setup_api
import argparse
from .src.args import CLIArgs
from .src.db import DBOperations as DB, DBGlobal as DBG, DatabaseConfig
from .src.environment import Environment
import logging
import logging.config
from .src.logging_formatter import ConsoleFormatter
from pathlib import Path
import shutil
import uvicorn


def main():
    """
    Collects CLI arguments and starts the chatbot.
    """
    cli_args = parse_args()

    start_chatbot(cli_args)


def parse_args(args=None):
    # get start up parameters
    arg_parser = argparse.ArgumentParser(description="Polybot API")

    for arg in CLIArgs.args.values():
        names_or_flags = arg.pop("name_or_flags", [])
        arg_parser.add_argument(*names_or_flags, **arg)

    # parse cli and board arguments
    cli_args = arg_parser.parse_args(args)
    return cli_args


def start_chatbot(cli_args):
    """
    Collects the configuration, sets up logging and database, and starts the API.
    """
    # set up instance directory in /home/jovyan/.polybot
    instance_dir = DatabaseConfig.db_path.value
    instance_dir.mkdir(parents=True, exist_ok=True)

    # format the board path
    board_path = Path(cli_args.board).resolve()

    # create new board path
    instance_board_path = instance_dir / board_path.name

    # copy the board to the instance directory
    # used to later copy the board into the db
    shutil.copy(board_path, instance_board_path)

    # configure all loggers
    setup_logging(default_level=cli_args.loglevel)
    # setup a logger
    logger = logging.getLogger(__name__)

    # log the configurations from cli and board
    logger.debug(f"startup args: {cli_args}")
    logger.debug(f"instance directory: {instance_dir}")

    # set the port
    port = 8501
    if cli_args.port:
        port = cli_args.port
    elif cli_args.public:
        port = 8499

    # setup database
    DB.setup_database()

    # store the global configuration
    args = {
        "board_path": str(board_path),
        "bot_name": cli_args.name,
        "chatbot_id": str(uuid.uuid4()),
        "chatlogs_path": str(cli_args.chatlogs),
        "current_card_id": str(cli_args.current_card_id),
        "debug_mode": int(1) if cli_args.debug else int(0),
        "downloadable": int(1) if cli_args.downloadable else int(0),
        "hide_function_calls": int(1) if cli_args.hide_function_calls else int(0),
        "instance_board_path": str(instance_board_path),
        "intro_narrow": cli_args.introtext,
        "intro_wide": cli_args.introtext,
        "parameters": int(1) if cli_args.parameters else int(0),
        "password": cli_args.password,  # str or None
        "port": port,
        "skip_intro": int(1) if cli_args.skiplogin else int(0),
    }
    DBG.set_config(**args)

    # create app
    app = setup_api(
        port=port, skip_login=cli_args.skiplogin, debug=True, password=cli_args.password
    )

    # print out URL as convenience
    logger.info(f"{args['bot_name']} is running on {Environment.get_app_url(port)}")

    # run server
    uvicorn.run(app, host="0.0.0.0", port=port)


def setup_logging(default_level=logging.DEBUG):
    """
    Setup logging for the application.

    Args:
        default_level (int, optional): Sets the logging level. Defaults to logging.DEBUG (10).
    """
    # setup necessary paths
    log_path = Path(DatabaseConfig.db_path.value / "logs")
    log_path.mkdir(exist_ok=True, parents=True)

    logging_config = {
        "version": 1,
        "formatters": {
            "console": {
                "()": ConsoleFormatter,
                "format": "%(message)s (%(filename)s:%(lineno)d)",
            },
            "file": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
                "level": default_level,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "file",
                "level": logging.DEBUG,
                "filename": log_path / f"{__name__}.log",
                "maxBytes": 1e6,
                "backupCount": 2,
            },
        },
        "loggers": {
            "": {  # Root Logger
                "handlers": ["console", "file"],
                "level": logging.DEBUG,
                "propagate": False,
            }
        },
    }

    logging.config.dictConfig(logging_config)


if __name__ == "__main__":
    main()
