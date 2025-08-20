# infrastructure
import base64
import mimetypes

from .chatbot_roles import ChatbotRoles
from datetime import datetime
from .db import (
    DBGlobal as DBG,
    DBHistory as DBH,
    DBBoard as DBB,
    DBChatbotConfig as DBC,
    DBSessions as DBS,
)
from .environment import Environment
from halerium_utilities.prompt import agents
import httpx
import json
import logging
from pathlib import Path
import ssl
from typing import AsyncGenerator, Dict, Any


class Chatbot:
    logger = logging.getLogger(__name__)

    @staticmethod
    def setup(session_id: str, session_data: dict):
        """
        Sets up the chatbot for a new session by adding the configuration to the db,
        and changing the system message in the db if necessary.
        """
        session_id,
        bot_type = session_data.get("bot_type")
        bot_name = session_data.get("bot_name")
        personality = session_data.get("setup_message")
        username = session_data.get("username")
        today = datetime.now().strftime("%Y-%m-%d")

        DBC.add(session_id, bot_type, bot_name, personality)

        DBB.update_board(
            session_id,
            ChatbotRoles.SYSTEM.value,
            f"\n\nDein Name ist: {bot_name}.\n\nHeute ist der {today}.",
        )

        if username:
            DBB.update_board(
                session_id,
                ChatbotRoles.SYSTEM.value,
                f"\n\nDein Gesprächspartner heißt {username}.",
            )

    @staticmethod
    async def evaluate(
        session_id: str, user_prompt: str, initial: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Evaluates user prompts via the prompt server

        Args:
            user_prompt (str): User prompt.

        Returns:
            str: Response.
        """
        Chatbot.logger.debug(f"Evaluating prompt for session {session_id}")
        Chatbot.logger.debug(f"Is initial message: {initial}")

        # append chatbot reponse to the history and the board
        # but only if this is not the initial prompt (otherwise it is already on the board)
        DBH.add_history_item(session_id, ChatbotRoles.USER.value, user_prompt)
        if not initial:
            DBB.update_board(session_id, ChatbotRoles.USER.value, user_prompt)

        # prompt model
        try:
            full_message = ""
            attachments = dict()

            # use the halerium prompt server for response generation
            endpoint = Environment.get_agents_endpoint_url()
            payload = Environment.build_agents_endpoint_payload(session_id)
            headers = Environment.build_prompt_server_headers()

            async for event in agents.call_agent_async(**payload, parse_data=True):
                Chatbot.logger.debug(f"received SSE: {event}")

                if event.event == "chunk":
                    full_message += event.data.get("chunk", "")

                if event.event == "function":
                    attachments[event.data["id"]] = {"function": event.data}

                if event.event == "function_output":
                    attachments[event.data["id"]]["function"]["content"] = event.data[
                        "content"
                    ]

                if event.event == "attachment":
                    attachments[event.data["filename"]] = {
                        mimetypes.guess_type(event.data["filename"])[0]: event.data[
                            "attachment"
                        ]
                    }

                yield vars(event)

            # append chatbot reponse to the history and the board
            DBH.add_history_item(session_id, ChatbotRoles.ASSISTANT.value, full_message)
            DBB.update_board(
                session_id, ChatbotRoles.ASSISTANT.value, full_message, attachments
            )

        except httpx.TimeoutException as e:
            Chatbot.logger.error(f"The model timed out: {e}")
            yield f"I'm sorry, the model timed out. Please try again."

        except Exception as e:
            Chatbot.logger.error(f"There has been an error evaluating a prompt: {e}")
            yield f"I'm sorry, there has been an error: {e}"

    @staticmethod
    async def transcribe_audio(path) -> AsyncGenerator[str | bool, None]:
        """
        Sends an audio file to the Whisper for transcription.

        Args:
            path (str): Path to the audio file.

        Returns:
            str: The transcript.
        """
        try:
            ssl_context = ssl.create_default_context()
            timeout = httpx.Timeout(60.0, connect=60.0)
            n_chunk = 0
            audio_b64 = base64.b64encode(open(path, "rb").read()).decode("utf-8")

            # use the halerium prompt server for response generation
            endpoint = Environment.get_models_endpoint_url()
            headers = Environment.build_prompt_server_headers()
            payload = Environment.build_models_endpoint_payload(audio_b64, "whisper")

            async with httpx.AsyncClient(verify=ssl_context, timeout=timeout) as client:
                async with client.stream(
                    method="POST", url=endpoint, json=payload, headers=headers
                ) as response:
                    async for chunk in response.aiter_lines():
                        Chatbot.logger.debug(f"transcript: {chunk}")
                        if "data: " in chunk:
                            content = json.loads(chunk[len("data: ") :])
                            n_chunk += 1
                            chunk = content.get("chunk")
                            completed = content.get("completed")
                            if chunk:
                                Chatbot.logger.debug(f"yielding transcript: {chunk}")
                                yield chunk
                            elif completed:
                                Chatbot.logger.debug(
                                    f"yielding status update: {completed}"
                                )
                                if content.get("error"):
                                    Chatbot.logger.error(
                                        f"There has been an error transcribing an audio file: {content.get('error')}"
                                    )
                                    yield f"I'm sorry, there has been an error transcribing your recording!"
                                yield completed

        except Exception as e:
            Chatbot.logger.error(
                f"There has been an error transcribing an audio file: {e}"
            )
            yield f"I'm sorry, there has been an error transcribing your recording!"
        else:
            # if transcription has been successful, delete the mp3
            is_debugging_session = DBG.get_config().get("debug_mode") == 1
            if not is_debugging_session:
                Path.unlink(Path(path))
            else:
                Chatbot.logger.debug(f"debugging session, not deleting {path}")

    @staticmethod
    def build_chat_log(session_id: str) -> dict:
        """
        Create a chat log file for the current session.

        Args:
            session_id (str): The ID of the current session.
        """
        # get data from db
        user_data = DBS.get_session_data(session_id)
        chat_history = DBH.get_history(session_id)

        # create chat log
        if user_data and chat_history:
            return {"user_data": user_data, "chat_history": chat_history}

        return {"user_data": None, "chat_history": None}
