# fastapi imports
from fastapi import (
    FastAPI,
    File,
    Form,
    Request,
    Response,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# infrastructure imports
import aiofiles
import asyncio
import argparse
from datetime import datetime
import json
import logging
import os
from pathlib import Path
from typing import List
from urllib.parse import unquote
from uuid import uuid4

# backend imports
from .src.args import CLIArgs
from .src.transcription_handler import atranscribe_audio
from .src.audio_processor import AudioProcessor
from .src.workflow_processor import WorkflowProcessor, WorkflowProcessorMode
from .src.board_utils import create_meeting_board, get_meeting_board_deep_link

# halerium utilities imports
from halerium_utilities.collab import CollabBoard


def parse_args(args=None):
    # get start up parameters
    arg_parser = argparse.ArgumentParser(description="Meeting Analyzer API")

    for arg in CLIArgs.args.values():
        names_or_flags = arg.pop("name_or_flags", [])
        arg_parser.add_argument(*names_or_flags, **arg)

    # parse cli and board arguments
    cli_args = arg_parser.parse_args(args)
    return cli_args


cli_args = parse_args()

# setup logging with debug level
logger = logging.getLogger(__name__)
logger.setLevel(cli_args.logger_level)
handler = logging.StreamHandler()
handler.setLevel(cli_args.logger_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Global variable to store transcripts
# TODO: needs to be changed at some point to a database or similar
transcripts = {}

# Global variable to store active sessions
# TODO: needs to be changed at some point to a database or similar
sessions = {}

meeting_template = Path(cli_args.board)

# create directories for storing audio files and meeting boards, define the app's root path
meetings_path = Path(cli_args.meetings_path)
meetings_path.mkdir(exist_ok=True, parents=True)
audio_upload_path = Path(cli_args.upload_path)
audio_upload_path.mkdir(exist_ok=True, parents=True)

# ports
port_app = cli_args.port
port_chatbot = cli_args.cbport

root_path = (
    f"/apps/{os.getenv('HALERIUM_ID')}/{str(port_app)}/"
    if os.getenv("HALERIUM_ID")
    else ""
)
frontend_path = Path(__file__).resolve().parent / "frontend"

# create the FastAPI app
app = FastAPI(root_path=root_path)


# mount static files and define templates directory
app.mount(
    "/static",
    StaticFiles(directory=frontend_path),
    name="static",
)
templates = Jinja2Templates(directory=frontend_path / "templates")

# chatbot link
chatbot_link = (
    f"{os.getenv('HALERIUM_BASE_URL')}/apps/{os.getenv('HALERIUM_ID')}/{port_chatbot}"
)
app_link = (
    f"{os.getenv('HALERIUM_BASE_URL')}/apps/{os.getenv('HALERIUM_ID')}/{port_app}"
)


def create_session():
    """
    Create a new session and return the session_id.

    Returns:
        dict: session_id
    """
    global sessions

    new_session_id = str(uuid4())
    sessions[new_session_id] = {
        "session_id": new_session_id,
        "start_time": None,
        "end_time": None,
        "active_ws": None,
        "board_path": None,
        "audio_processor": None,
    }
    return {"session_id": new_session_id}


def is_valid_session(session_id):
    """
    Check if a session_id is valid.

    Args:
        session_id (str): The session_id to check.

    Returns:
        bool: True if the session_id is valid, False otherwise.
    """
    global sessions
    return session_id in sessions


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):

    session = create_session()
    response = templates.TemplateResponse(
        "mode-selector.html",
        {
            "request": request,
            "chatbot_link": chatbot_link,
            "session_id": session["session_id"],
        },
    )

    return response


@app.get("/meeting/{session_id}", response_class=HTMLResponse)
async def meeting(request: Request, session_id: str):

    if not is_valid_session(session_id):
        return Response("Invalid session id.", status_code=400)

    return templates.TemplateResponse(
        "meeting.html",
        {
            "request": request,
            "chatbot_link": chatbot_link,
            "session_id": session_id,
        },
    )


@app.websocket("/meeting/{session_id}/record")
async def record(websocket: WebSocket, session_id: str):
    """
    Websocket connection for the audio stream.
    """
    if not is_valid_session(session_id):
        await websocket.close()
        return Response("Invalid session id.", status_code=400)

    global sessions, transcripts
    await websocket.accept()
    audio_processor = None

    # check if session_id is valid
    if session_id not in sessions:
        logger.error(f"Invalid session_id: {session_id}")
        await websocket.close()

    # check if session is already active
    if sessions[session_id]["active_ws"]:
        logger.error(f"Session {session_id} is already active.")
        await websocket.close()
    else:
        logger.info(f"Session {session_id} started.")
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sessions[session_id]["active_ws"] = websocket
        sessions[session_id]["start_time"] = start_time

    try:
        while True:
            # receive data
            data = await websocket.receive()

            # start/stop recording
            if "text" in data:

                # if "ping" is received, send "pong":
                if data["text"] == "ping":
                    await websocket.send_text("pong")
                    continue

                message = json.loads(data.get("text"))

                if message["type"] == "audio-start":
                    samplerate = message["samplerate"]
                    audio_processor = AudioProcessor(int(samplerate), session_id)
                    sessions[session_id]["audio_processor"] = audio_processor
                    logger.debug(
                        f"{session_id} started recording ({samplerate} Hz -> {samplerate * 16/8} bytes/sec)"
                    )

                elif message["type"] == "audio-end":
                    logger.debug(f"{session_id} stopped recording")
                    sessions[session_id]["audio_processor"].is_recording = False
                    filename = sessions[session_id]["audio_processor"].export_to_mp3()
                    logger.debug(f"{session_id} created file: {filename}")
                    sessions[session_id]["mp3_name"] = filename
                    sessions[session_id]["audio_processor"] = None

            # receive audio data
            elif "bytes" in data:
                if (
                    sessions[session_id]["audio_processor"]
                    and sessions[session_id]["audio_processor"].is_recording
                ):
                    byte_data = data.get("bytes")
                    sessions[session_id]["audio_processor"].write_chunk(byte_data)

    except WebSocketDisconnect:
        logger.debug(f"{session_id}: AudioWebSocket disconnected.")

    except RuntimeError as e:
        logger.error(f"{session_id}: AudioWebsocket RuntimeError: {e}")

    finally:
        # remove from active sessions
        sessions[session_id]["active_ws"] = None


@app.get("/meeting/{session_id}/transcribe")
async def transcribe(request: Request, session_id: str):
    """
    Converts the 16-bit PCM audio data to an mp3 and transcribes it.

    Args:
        session_id (str): The user session_id
    """
    if not is_valid_session(session_id):
        return Response("Invalid session id.", status_code=400)

    global transcripts, sessions

    # if there is no filename, but still an audio recorder, then the websocket connection apparently failed to sent the audio-end message
    # and we still need convert the raw temp file to an mp3
    if (
        not "mp3_name" in sessions[session_id]
        and sessions[session_id]["audio_processor"]
    ):
        logger.debug(f"{session_id} stopped recording")
        filename = sessions[session_id]["audio_processor"].export_to_mp3()
        (
            logger.debug(f"{session_id} created potentially partial file: {filename}")
            if filename
            else logger.error(f"Failed to export temp file to mp3 for {session_id}")
        )

        sessions[session_id]["mp3_name"] = filename

    # if there is a filename the audio file was already created
    elif "mp3_name" in sessions[session_id] and sessions[session_id]["mp3_name"]:
        logger.debug(f"Found existing mp3 file: {sessions[session_id]['mp3_name']}")

    try:
        transcript = ""
        with open(sessions[session_id]["mp3_name"], "rb") as uploaded_file:

            logger.debug(
                f"Transcribing recorded audio file: {sessions[session_id]['mp3_name']}"
            )
            transcript = await atranscribe_audio(uploaded_file)

        transcripts[session_id] = transcript

    except Exception as e:
        logger.error(f"Error transcribing audio file: {e}")
        transcripts[session_id] = "Error transcribing audio file."
        return {"status": "error", "result": "Error transcribing audio file."}
    else:
        # send ready message to client
        return {"status": "success", "result": "Transcription successful."}


@app.get("/meeting/{session_id}/analyze_transcript", response_class=HTMLResponse)
async def analyze_transcript(request: Request, session_id: str):

    if not is_valid_session(session_id):
        return Response("Invalid session id.", status_code=400)

    # get the transcript from the current session
    global transcripts, sessions
    transcript = transcripts[session_id]

    # create a meeting board from the transcript
    meeting_board_path = create_meeting_board(
        transcript, meetings_path=meetings_path, meeting_template=meeting_template
    )

    sessions[session_id]["board_path"] = meeting_board_path

    # get the deep link to the meeting board
    deep_link = get_meeting_board_deep_link(meeting_board_path)

    # create a workflow processor
    workflow_processor = WorkflowProcessor(
        board_path=meeting_board_path, session_id=session_id
    )

    # returns two dicts of card_ids and corresponding prompt outputs / errors
    result, errors = workflow_processor.execute(mode=WorkflowProcessorMode.PREPROCESS)

    return templates.TemplateResponse(
        "analysis.html",
        {
            "request": request,
            "chatbot_link": chatbot_link,
            "analysis_output": result,
            "meeting_board_path": meeting_board_path,
            "deep_link": deep_link,
            "transcript": transcript,
            "session_id": session_id,
            "error_cards": errors if errors else None,
        },
    )


@app.post("/upload/{session_id}", response_class=HTMLResponse)
async def upload(
    request: Request, session_id: str, fileInputs: list[UploadFile] = File(...)
):

    if not is_valid_session(session_id):
        return Response("Invalid session id.", status_code=400)

    file_names = [file.filename for file in fileInputs]
    chunk_byte_size = 1024 * 1024  # 1 MB

    # files will be uploaded in chunks to avoid memory issues
    async def save_file(file: UploadFile, path: Path):
        async with aiofiles.open(path, "wb") as f:
            while content := await file.read(chunk_byte_size):
                await f.write(content)

    # files will be uploaded in parallel to speed up the process
    tasks = []
    for file in fileInputs:
        file_path = Path(audio_upload_path / file.filename)
        if not file_path.exists():
            tasks.append(save_file(file, file_path))

    await asyncio.gather(*tasks)

    logger.debug(f"Uploaded files: {file_names}")

    return templates.TemplateResponse(
        "uploaded_files_list.html",
        {
            "request": request,
            "chatbot_link": chatbot_link,
            "file_names": file_names,
            "session_id": session_id,
        },
    )


@app.post("/upload/{session_id}/transcribe_and_analyze_files")
async def transcribe_and_analyze_files(
    request: Request, session_id: str, fileNames: List[str] = Form(...)
):
    if not is_valid_session(session_id):
        return Response("Invalid session id.", status_code=400)
    if not fileNames:
        return {"error": "No file selected"}

    full_transcript = ""

    logger.debug(f"Requested transcription for files: {fileNames}")

    # get the transcript for all files
    for filename in fileNames:
        audiofile_path = os.path.join(audio_upload_path, filename)
        with open(audiofile_path, "rb") as uploaded_file:

            # get the transcript for all files
            logger.debug(f"Transcribing uploaded audio file: {audiofile_path}")
            transcript = await atranscribe_audio(uploaded_file)

        full_transcript += "\n\n\n" + transcript

    # create a meeting board from the transcript
    meeting_board_path = create_meeting_board(
        full_transcript, meetings_path=meetings_path, meeting_template=meeting_template
    )

    sessions[session_id]["board_path"] = meeting_board_path

    # get the deep link to the meeting board
    deep_link = get_meeting_board_deep_link(meeting_board_path)

    # create a workflow processor
    workflow_processor = WorkflowProcessor(
        board_path=meeting_board_path, session_id=session_id
    )
    # returns two dicts of card_ids and corresponding prompt outputs / errors
    result, errors = workflow_processor.execute(mode=WorkflowProcessorMode.PREPROCESS)

    return templates.TemplateResponse(
        "analysis.html",
        {
            "request": request,
            "chatbot_link": chatbot_link,
            "analysis_output": result,
            "meeting_board_path": meeting_board_path,
            "deep_link": deep_link,
            "transcript": full_transcript,
            "session_id": session_id,
            "error_cards": errors if errors else None,
        },
    )


@app.post("/update_board/{session_id}")
async def update_board(
    request: Request,
    session_id: str,
):

    if not is_valid_session(session_id):
        return Response("Invalid session id.", status_code=400)

    global sessions
    r = await request.json()

    meeting_board_path = sessions[session_id].get("board_path")
    modified_analysis = r.get("approved")

    if meeting_board_path and modified_analysis:
        board = CollabBoard(meeting_board_path, pull_on_init=True)

        for card_id, update in modified_analysis.items():
            board.update_card(
                {"id": card_id, "type_specific": {"prompt_output": update}}
            )
            board.push()

        return {"status": "success", "message": "Board successfully modified."}

    return {"status": "error", "message": "No board path or modified analysis found."}


@app.post("/approve_and_postprocess/{session_id}")
async def approve_and_postprocess(
    request: Request,
    session_id: str,
):

    if not is_valid_session(session_id):
        return Response("Invalid session id.", status_code=400)

    r = await request.json()

    global sessions

    meeting_board_path = sessions[session_id].get("board_path")
    approved_analysis = r.get("approved")
    # transcript = r.get("transcript")

    if meeting_board_path and approved_analysis:
        board = CollabBoard(meeting_board_path, pull_on_init=True)

        summaries = ""
        for card_id, update in approved_analysis.items():
            board.update_card(
                {"id": card_id, "type_specific": {"prompt_output": update}}
            )
            board.push()

            summaries += update + "\n\n"

        # post-process the transcript
        workflow_processor = WorkflowProcessor(
            board_path=meeting_board_path, session_id=session_id
        )
        _, errors = workflow_processor.execute(mode=WorkflowProcessorMode.POSTPROCESS)

        if errors:
            return {
                "status": "error",
                "message": errors,  # errors: {"card_id": "error message"}
            }
        else:
            return {
                "status": "success",
                "message": "Analysis successfully postprocessed.",
            }

    return {"status": "error", "message": "No board path or approved analysis found."}


@app.get("/success")
async def success(request: Request, deep_link: str, success: bool, message: str = ""):

    # message is urlencoded string
    message = unquote(message)

    if isinstance(message, str) and not success:
        try:
            message = json.loads(message)
        except json.JSONDecodeError as e:
            logger.warning(f'Parsing error for error message: "{message}"')
            logger.warning(f"Error: {e}")
            logger.warning(f'Wrapping message in "error" key')
            message = {"error": message}

    if success:

        return templates.TemplateResponse(
            "success.html",
            {
                "request": request,
                "chatbot_link": chatbot_link,
                "deep_link": deep_link,
                "message": message,
            },
        )

    else:

        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "chatbot_link": chatbot_link,
                "deep_link": deep_link if not deep_link == "None" else None,
                "message": message,
            },
        )


def main():

    uvicorn.run(app, host="0.0.0.0", port=port_app, log_level=cli_args.logger_level)
