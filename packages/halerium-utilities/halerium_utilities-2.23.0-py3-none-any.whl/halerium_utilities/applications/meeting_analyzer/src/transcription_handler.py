from .environment import HaleriumEnvironment
from halerium_utilities.prompt.models import call_model
from halerium_utilities.utils import sse
import httpx
import json
import logging

logger = logging.getLogger(__name__)


async def atranscribe_audio(file_stream: bytes) -> str:
    """
    Transcribe audio file using Deepgram's Nova2 model.

    Args:
        file_stream (bytes): Audio file stream

    Returns:
        str: Transcript of the audio file
    """

    env = HaleriumEnvironment()
    combined_transcript = ""

    async with httpx.AsyncClient() as httpx_client:
        files = {"file": ("filename", file_stream, "audio/wav")}
        json_payload = {
            "model_id": "nova2",
            "tenant": env.tenant,
            "workspace": env.workspace,
            "body": {},
        }
        data = {"json_data": json.dumps(json_payload)}  # Convert JSON payload to string

        async with httpx_client.stream(
            url=env.prompt_url + "/models/upload",
            method="POST",
            files=files,
            data=data,
            headers=env.headers,
            timeout=120,
        ) as response:
            async for event in sse.parse_sse_response_async(response):
                if event.event == "chunk":
                    data = json.loads(event.data)
                    paragraphs = data.get("paragraphs")
                    if isinstance(paragraphs, dict):
                        transcript = paragraphs.get("transcript")
                        if transcript is not None:
                            combined_transcript += transcript
                        else:
                            print("Key 'transcript' not found in 'paragraphs'")
                elif event.event == "conclusion":
                    result = json.loads(event.data)
                    if "error" in result:
                        print(result["error"])
                    break

    print(f"Transcription tenant={env.tenant} and workspace={env.workspace} complete.")

    return combined_transcript


def transcribe_audio(audio_b64: str) -> str:
    """
    Transcribe audio file using Deepgram's Nova2 model.

    Args:
        audio_b64 (str): Base64 encoded audio file

    Returns:
        str: Transcript of the audio file
    """

    body = {
        "audio": audio_b64,
        "diarize": True,
    }
    r = call_model("nova2", body=body, parse_data=True)

    combined_transcript = ""
    for sse in r:
        paragraphs = sse.data.get("paragraphs")
        if isinstance(paragraphs, dict):
            transcript = paragraphs.get("transcript")
            if transcript is not None:
                ans += transcript

    return combined_transcript
