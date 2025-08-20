# api.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .src.routers.http import router as http
from .src.routers.websockets import router as websockets

# infrastructure
from .src.environment import Environment
import logging
from pathlib import Path


def setup_api(port: int | str, skip_login: bool = False, debug: bool = True, password: str = None):
    logger = logging.getLogger(__name__)
    logger.debug("Creating fastapi app")

    app = FastAPI(debug=debug)
    if Environment._is_local():
        app.mount(
            "/static",
            StaticFiles(directory=Path(__file__).resolve().parent / "frontend/static"),
            name="static",
        )
    else:
        app.mount(
            "/static",
            StaticFiles(directory=Path(__file__).resolve().parent / "frontend"),
            name="static",
        )
    app.root_path = Environment.get_app_root_path(port)
    logger.debug(f"App root path: {app.root_path}")

    app.include_router(http)
    app.include_router(websockets)

    # Add password to the configuration if provided
    if password:
        app.state.password = password
    else:
        app.state.password = None

    return app
