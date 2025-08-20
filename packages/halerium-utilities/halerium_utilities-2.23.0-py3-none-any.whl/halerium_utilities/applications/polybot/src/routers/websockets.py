# api
import asyncio
from ..audio_processor import AudioProcessor
from ..chatbot import Chatbot
from datetime import datetime
from ..db import DBSessions as DBS, DBOperations as DBO, DBBoard as DBB, DBGlobal as DBG
from ..environment import Environment
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Query,
    status,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from halerium_utilities.board import Board
import io
import json
import logging
from pathlib import Path
import re
import requests
import time
from typing import Annotated


router = APIRouter(
    prefix="/ws",
    tags=["websocket"],
    responses={404: {"description": "Not found"}},
)


async def get_session_id(
    websocket: WebSocket,
    chatbot_session_id: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
):
    """
    Checks websocket connection for sessionID token.
    If none, raises an exception and rejects the connection.

    Args:
        websocket (WebSocket): New websocket connection
        chatbot_session_id (Annotated[str  |  None, Cookie, optional): Expected session token. Defaults to None.
        token (Annotated[str  |  None, Query, optional): Expected session token. Defaults to None.

    Raises:
        WebSocketException: If no token or session was found.

    Returns:
        str: Session id
    """
    logger = logging.getLogger(__name__)
    # logger.info(f"Received cookies: {websocket.cookies}")
    # logger.info(f"Received chatbot_session_id: {chatbot_session_id}")
    # logger.info(f"Received token: {token}")

    if chatbot_session_id is None and token is None:
        logger.error("No Session ID provided. Closing websocket.")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return chatbot_session_id or token


@router.websocket("/text")
async def text_messages(
    websocket: WebSocket, session_id: Annotated[str, Depends(get_session_id)]
):
    """
    Websocket connection for the chat function. Waits for a prompt and then queries the chatbot.
    Output function is a generator to allow for token-wise "streaming".
    """
    logger = logging.getLogger(__name__)
    dbg_config = DBG.get_config()
    if not DBS.is_active_session(session_id):
        logger.error(
            f"Session ID {str(session_id)} not found in active sessions. Closing websocket."
        )
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    else:
        await websocket.accept()
        await asyncio.sleep(0)

        logger.debug(f"{session_id} TextWebsocket connected.")

    try:
        while True:
            # get prompt and timestamp
            data = await websocket.receive()
            # prompt = await websocket.receive_text()

            if "text" in data:
                text_string = json.loads(data.get("text"))

                if isinstance(text_string, str):
                    text_json = json.loads(text_string)
                else:
                    text_json = text_string

                data_type = text_json.get("type")
                sid = text_json.get("session_id")
                query = text_json.get("query")
                is_initial_prompt = text_json.get("isInitialPrompt", False)
                prompt = data.get("text")

                if data_type == "ping":
                    await websocket.send_json(
                        {"event": "pong", "data": {"chunk": "<pong>"}}
                    )
                    continue

                if data_type == "prompt":
                    prompt = query
                    logger.info(
                        f'Session {sid} prompt @ {datetime.now().strftime("%Y-%m-%dT%H:%M:%S:%f")}',
                    )
                    now = time.time()
                    full_message = ""
                    n_token = 0
                    async for event in Chatbot.evaluate(
                        session_id, prompt, initial=is_initial_prompt
                    ):

                        # do not send function calls if hide_function_calls is set
                        if dbg_config.get("hide_function_calls") and (
                            event["event"] == "function"
                            or event["event"] == "function_output"
                        ):
                            logger.debug("hiding function call or output")
                            continue

                        # do not sent empty chunks
                        if event["event"] == "chunk" and not event["data"].get("chunk"):
                            logger.debug("skipping empty chunk")
                            continue

                        # do not send markdown function call labels
                        regex = r"!\[.*?\]\((function:.*?)\)"
                        if event["event"] == "chunk" and re.search(
                            regex, event["data"].get("chunk", "")
                        ):
                            logger.debug("skipping markdown function call label")
                            continue

                        # if it's the first token, send the <sos> token as well
                        if n_token == 0:
                            # begin message
                            logger.debug("sending <sos> token")
                            await websocket.send_json(
                                {"event": "chunk", "data": {"chunk": "<sos>"}}
                            )

                        logger.debug(f"sending event: {event}")
                        await websocket.send_json(event)

                        if event["event"] == "chunk":
                            full_message += event["data"].get("chunk", "")

                        # This also counts the attachment events etc.
                        # But as it's purpose is only logging, it may be ok
                        n_token += 1

                        if event["event"] == "conclusion":
                            await websocket.send_json(
                                {"event": "chunk", "data": {"chunk": "<eos>"}}
                            )

                            # text2speech
                            # logger.info("Generating audio...")
                            # voice = Chatbot.text_to_speech(full_message)
                            # await websocket.send_json({"event": "audio", "data": {"audio": base64.b64encode(voice).decode()}})

                    # generation time
                    delta = time.time() - now

                    logger.info(
                        f'finished @ {datetime.now().strftime("%Y-%m-%dT%H:%M:%S:%f")}'
                    )

                    # timing information
                    if n_token > 0:
                        logger.debug(
                            f"received and sent {n_token} token in {round(delta, 3)} s ({round(delta/n_token, 3)} s/token)"
                        )

    except WebSocketDisconnect:
        logger.debug(f"TextWebsocket for session {session_id} disconnected")

    except Exception as e:
        logger.error(f"TextWebsocket RuntimeError", exc_info=e)

    finally:
        chatlogs_path = None
        if (
            DBG.get_config().get("chatlogs_path")
            and DBG.get_config().get("chatlogs_path") != "None"
        ):
            chatlogs_path = Path(DBG.get_config().get("chatlogs_path"))

        if chatlogs_path:
            logger.debug(f"Chatlogs path: {chatlogs_path}")

            # make sure chat log paths exist
            json_files = "json"
            board_files = "boards"
            Path.mkdir(chatlogs_path / json_files, exist_ok=True, parents=True)
            Path.mkdir(chatlogs_path / board_files, exist_ok=True, parents=True)

            # build the chat log and chat board
            chat_log = Chatbot.build_chat_log(session_id)
            chat_board = DBB.get_board(session_id)

            # save chat log and chat board
            with io.StringIO(json.dumps(chat_board)) as f:
                chat_board = Board.from_json(f)

            now = datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")
            with open(
                chatlogs_path / Path(f"{json_files}/{now}_{session_id}.json"), "w"
            ) as f:
                json.dump(chat_log, f, indent=4, ensure_ascii=False)

            with open(
                chatlogs_path / Path(f"{board_files}/{now}_{session_id}.board"), "w"
            ) as f:
                chat_board.to_json(f)

            logger.debug(f"generated chatlog for session {session_id}")

        else:
            logger.debug("chatlogs_path not set: chatlogs will not be saved")

        # kill session kernel
        path = Path(DBG.get_config().get("board_path")).relative_to(
            Path.home()
        ).parent / Path(session_id + ".board")
        env_params = Environment.get_env_params()
        endpoint = Environment.get_kernel_cleanup_endpoint_url()
        headers = {"halerium-runner-token": env_params.get("runner_token", "")}
        payload = {"runner_id": env_params.get("runner_id", ""), "path": str(path)}

        response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            if response.json().get("success") == True:
                logger.info(
                    f"killed kernel for {path}: {response.json().get('result')}"
                )
            else:
                logger.error(
                    f"kernel for {path} could not be killed: Cleanup function returned {response.json().get('result')}"
                )
        else:
            logger.error(
                f"kernel for {path} could not be killed: Endpoint returned {response.status_code}"
            )

        # delete user data from database
        DBO.delete_user_data(session_id)

        logger.info(f"Session {session_id} terminated")


@router.websocket("/voice")
async def audio_messages(
    websocket: WebSocket, session_id: Annotated[str, Depends(get_session_id)]
):
    """
    Websocket connection for the audio stream.
    """
    logger = logging.getLogger(__name__)

    if not DBS.is_active_session(session_id):
        logger.error(
            f"Session ID {str(session_id)} not found in active sessions. Closing websocket."
        )
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    else:
        await websocket.accept()
        await asyncio.sleep(0)

    try:
        total_bytes = 0

        while True:
            # receive data
            data = await websocket.receive()

            # start/stop recording
            if "text" in data:
                message = json.loads(data.get("text"))

                if message["type"] == "audio-start":
                    samplerate = message["samplerate"]
                    audio_processor = AudioProcessor(int(samplerate), session_id)
                    logger.debug(f"User started recording. Samplerate: {samplerate}")

                elif message["type"] == "audio-end":
                    logger.debug("Stopped recording")
                    filename = audio_processor.export_mp3()
                    logger.debug(f"Received filename: {filename}")
                    try:
                        transcript = ""
                        async for token in Chatbot.transcribe_audio(filename):
                            if isinstance(token, str):
                                transcript += token
                                await websocket.send_json(
                                    {"event": "chunk", "data": {"chunk": token}}
                                )
                            elif isinstance(token, bool):
                                continue  # boolean is a status update
                        logger.debug(f"Transcript: {transcript}")
                    except Exception as e:
                        logger.error(f"Error transcribing voice message: {e}")
                        await websocket.send_text("Error transcribing voice message")
                        continue
                    else:
                        # send transcript to frontend
                        # await websocket.send_text(transcript)
                        continue

            # receive audio data
            elif "bytes" in data:
                if audio_processor and audio_processor.is_recording:
                    audio_chunk = data.get("bytes")
                    total_bytes += len(audio_chunk)
                    audio_processor.add_chunk(audio_chunk)

    except WebSocketDisconnect:
        logger.debug(f"AudioWebSocket for session {session_id} disconnected.")

    except RuntimeError as e:
        logger.error(f"AudioWebsocket RuntimeError: {e}")

    finally:
        if audio_processor:
            _ = audio_processor.export_mp3()
