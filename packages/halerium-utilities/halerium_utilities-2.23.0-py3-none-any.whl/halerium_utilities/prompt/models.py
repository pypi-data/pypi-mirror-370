import httpx
import json
import os
from typing import Any, Dict
from urllib.parse import urljoin

from halerium_utilities.utils.sse import parse_sse_response, parse_sse_response_async


def _prepare_model_request(model_name: str, body: dict):
    """
    Prepare the httpx streaming parameters to load model results.

    Parameters
    ----------
    model_name The name of the model.
    body The body dict to be passed to the model.

    Returns
    -------
    A dict containing the httpx stream parameters (kwargs) for streaming model results.

    """

    tenant = os.getenv("HALERIUM_TENANT_KEY", "")
    workspace = os.getenv("HALERIUM_PROJECT_ID", "")
    runner_id = os.getenv("HALERIUM_ID", "")
    base_url = os.getenv("HALERIUM_BASE_URL", "")
    url = urljoin(
        base_url,
        "/api"
        f"/tenants/{tenant}"
        f"/projects/{workspace}"
        f"/runners/{runner_id}"
        "/prompt/models",
    )

    headers = {"halerium-runner-token": os.getenv("HALERIUM_TOKEN", "")}

    payload = {
        "model_id": model_name,
        "body": body,
    }

    return dict(
        method="POST",
        url=url,
        headers=headers,
        json=payload,
        timeout=600,
    )


async def call_model_async(
    model_name: str, body: Dict[str, Any], parse_data: bool = False
):
    """Call model asynchronously from a Halerium runner.

    Calls the specified model with the given body.

    Parameters
    ----------
    model_name: str
        The model to use. Currently supported are "chat-gpt-35", "chat-gpt-40",
        "chat-gpt-40-o", "llama3", "snowflake-arctic", "mixtral", "dall-e",
        "stable-diffusion", "ada2-embedding", "whisperx", "google-vision", "whisper", "nova2".
    body: Dict[str, Any]
        The body for the model's request.
        See the examples.
    parse_data: bool, optional
        Whether to parse the SSE event data as json strings.
        The default is False.

    Returns
    -------
    async_generator
        The generator of the models answer as SSE events.

    Request Body Templates
    ----------------------
    all chat-gpt based models, llama models and mistral chat models:
        {
            "messages": [{"role": "user", "content": "Hi!"}],
            "temperature": 0
        }

    snowflake-arctic:
        {
            "prompt": "User: Hi! AI:",
            "temperature": 0
        }

    dall-e:
        {
            "prompt": "Lion vs. Tiger",
            "size": "1024x1024"
        }

    stable-diffusion:
       {
            "prompt": {"positive_prompt": "Lion vs. Tiger", "negative_prompt": "Nudes"},
            "size": (1024, 1024)
        }

    ada2-embedding:
        {
            "text_chunks": ["My father is the king"]
        }

    whisperx, whisper:
        {
            "audio": "Base64 encoded audio data",
            "language": "en",
        }

     nova2:
        {
            "audio": "Base64 encoded audio data",
            "language": "en",
            "diarize": False
            # diarize True if you want to diarize the audio
        }

    google-vision:
        {
            "image": "Base64 encoded image data",
            "images: "List of Base64 encoded image data", #  only used if "image" is not given.
            "features": [{"type": "TEXT_DETECTION"}]
            # use "DOCUMENT_TEXT_DETECTION" for dense documents
        }

    mistral-ocr:
        {
            "document": "Base64 encoded pdf",
            "image": "Base64 encoded image data",  # only used if "document" is not given
            "images: "List of Base64 encoded image data", #  only used if "image" is not given.
        }

    Examples
    --------
    >>> body = {"messages": [{"role": "user", "content": "Hi!"}], "temperature": 0}
    >>> gen = call_model_async("chat-gpt-35", body=body)
    >>> async for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Hello", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='chunk', data='{"chunk": "!", "created": "2023-11-28T16:32:56.724526"}')
    namespace(event='chunk', data='{"chunk": " How", "created": "2023-11-28T16:32:56.724673"}')
    namespace(event='chunk', data='{"chunk": " can", "created": "2023-11-28T16:32:56.724804"}')
    namespace(event='chunk', data='{"chunk": " I", "created": "2023-11-28T16:32:56.724941"}')
    namespace(event='chunk', data='{"chunk": " assist", "created": "2023-11-28T16:32:56.725077"}')
    namespace(event='chunk', data='{"chunk": " you", "created": "2023-11-28T16:32:56.725220"}')
    namespace(event='chunk', data='{"chunk": " today", "created": "2023-11-28T16:32:56.725354"}')
    namespace(event='chunk', data='{"chunk": "?", "created": "2023-11-28T16:32:56.725485"}')
    namespace(event='chunk', data='{"chunk": "", "created": "2023-11-28T16:32:56.725611"}')


    >>> body = {"prompt": "User: Hi! AI:", "temperature": 0}
    >>> gen = call_model_async("snowflake-arctic", body=body)
    >>> async for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Hello", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='chunk', data='{"chunk": "!", "created": "2023-11-28T16:32:56.724526"}')
    namespace(event='chunk', data='{"chunk": " How", "created": "2023-11-28T16:32:56.724673"}')
    namespace(event='chunk', data='{"chunk": " can", "created": "2023-11-28T16:32:56.724804"}')
    namespace(event='chunk', data='{"chunk": " I", "created": "2023-11-28T16:32:56.724941"}')
    namespace(event='chunk', data='{"chunk": " assist", "created": "2023-11-28T16:32:56.725077"}')
    namespace(event='chunk', data='{"chunk": " you", "created": "2023-11-28T16:32:56.725220"}')
    namespace(event='chunk', data='{"chunk": " today", "created": "2023-11-28T16:32:56.725354"}')
    namespace(event='chunk', data='{"chunk": "?", "created": "2023-11-28T16:32:56.725485"}')
    namespace(event='chunk', data='{"chunk": "", "created": "2023-11-28T16:32:56.725611"}')
    namespace(event='conclusion', data={'completed': True})


    >>> body = {"prompt": "A beautiful landscape", "size": "1024x1024"}
    >>> gen = call_model_async("dall-e", body=body)
    >>> async for event in gen: print(event)
    namespace(event='attachment', data='{"attachment": "Base64 attachment", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='chunk', data='{"chunk": "![output_image.png](attachment:output_image.png)", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='conclusion', data={'completed': True})


    >>> body = {"prompt": {"positive_prompt": "Lion vs. Tiger", "negative_prompt": "Nudes"}, "size": "1024x1024"}
    >>> gen = call_model_async("stable-diffusion", body=body)
    >>> async for event in gen: print(event)
    namespace(event='attachment', data='{"attachment": "Base64 attachment", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='chunk', data='{"chunk": "![output_image.png](attachment:output_image.png)", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='conclusion', data={'completed': True})


    >>> body = {"text_chunks": ["My father is the king"]}
    >>> gen = call_model_async("ada2-embedding", body=body)
    >>> async for event in gen: print(event)
    namespace(event='embedding', data='{"index": "0", "embedding": "Embedding generated", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='conclusion', data={'completed': True})


    >>> body = {"audio": "Base64 encoded audio data", "language": "en"}
    >>> gen = call_model_async("whisperx", body=body)
    >>> async for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Transcription generated", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='conclusion', data={'completed': True})


    >>> body = {"audio": "Base64 encoded audio data", "language": "en"}
    >>> gen = call_model_async("whisper", body=body)
    >>> async for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Transcription generated", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='conclusion', data={'completed': True})


    >>> body = {"audio": "Base64 encoded audio data", "language": "en", "diarize": False}
    >>> gen = call_model_async("nova2", body=body)
    >>> async for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Transcription generated", "created": "2023-11-28T16:32:56.724070", "paragraphs": "Transcript generated in paragraphs if diarize is True"}')
    namespace(event='conclusion', data={'completed': True})


    >>> body = {"image": "Base64 encoded image data", "features": [{"type": "LABEL_DETECTION"}]}
    >>> gen = call_model_async("google-vision", body=body)
    >>> async for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Image analysis generated", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='conclusion', data={'completed': True})
    """

    async with httpx.AsyncClient() as httpx_client:
        async with httpx_client.stream(
            **_prepare_model_request(model_name, body)
        ) as response:
            async for event in parse_sse_response_async(response):
                if parse_data:
                    event.data = json.loads(event.data)
                yield event


def call_model(model_name: str, body: Dict[str, Any], parse_data: bool = False):
    """Call model from a Halerium runner.

    Calls the specified model with the given body.

    Parameters
    ----------
    model_name: str
        The model to use. Currently supported are "chat-gpt-35", "chat-gpt-40",
        "chat-gpt-40-o", "llama3", "snowflake-arctic", "mixtral", "dall-e",
        "stable-diffusion", "ada2-embedding", "whisperx", "google-vision", "whisper", "nova2".
    body: Dict[str, Any]
        The body for the model's request.
        See the examples.
    parse_data: bool, optional
        Whether to parse the SSE event data as json strings.
        The default is False.

    Returns
    -------
    generator
        The generator of the models answer as SSE events.

    Request Body Templates
    ----------------------
    all chat-gpt based models, llama models and mistral chat models:
        {
            "messages": [{"role": "user", "content": "Hi!"}],
            "temperature": 0
        }

    snowflake-arctic:
        {
            "prompt": "User: Hi! AI:",
            "temperature": 0
        }

    dall-e:
        {
            "prompt": "Lion vs. Tiger",
            "size": "1024x1024"
        }

    stable-diffusion:
       {
            "prompt": {"positive_prompt": "Lion vs. Tiger", "negative_prompt": "Nudes"},
            "size": (1024, 1024)
        }

    ada2-embedding:
        {
            "text_chunks": ["My father is the king"]
        }

    whisperx, whisper:
        {
            "audio": "Base64 encoded audio data",
            "language": "en",
        }

     nova2:
        {
            "audio": "Base64 encoded audio data",
            "language": "en",
            "diarize": False
            # diarize True if you want to diarize the audio
        }

    google-vision:
        {
            "image": "Base64 encoded image data",
            "images: "List of Base64 encoded image data", #  only used if "image" is not given.
            "features": [{"type": "TEXT_DETECTION"}]
            # use "DOCUMENT_TEXT_DETECTION" for dense documents
        }

    mistral-ocr:
        {
            "document": "Base64 encoded pdf",
            "image": "Base64 encoded image data",  # only used if "document" is not given
            "images: "List of Base64 encoded image data", #  only used if "image" is not given.
        }

    Examples
    --------
    >>> body = {"messages": [{"role": "user", "content": "Hi!"}], "temperature": 0}
    >>> gen = call_model("chat-gpt-35", body=body)
    >>> for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Hello", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='chunk', data='{"chunk": "!", "created": "2023-11-28T16:32:56.724526"}')
    namespace(event='chunk', data='{"chunk": " How", "created": "2023-11-28T16:32:56.724673"}')
    namespace(event='chunk', data='{"chunk": " can", "created": "2023-11-28T16:32:56.724804"}')
    namespace(event='chunk', data='{"chunk": " I", "created": "2023-11-28T16:32:56.724941"}')
    namespace(event='chunk', data='{"chunk": " assist", "created": "2023-11-28T16:32:56.725077"}')
    namespace(event='chunk', data='{"chunk": " you", "created": "2023-11-28T16:32:56.725220"}')
    namespace(event='chunk', data='{"chunk": " today", "created": "2023-11-28T16:32:56.725354"}')
    namespace(event='chunk', data='{"chunk": "?", "created": "2023-11-28T16:32:56.725485"}')
    namespace(event='chunk', data='{"chunk": "", "created": "2023-11-28T16:32:56.725611"}')


    >>> body = {"prompt": "User: Hi! AI:", "temperature": 0}
    >>> gen = call_model("snowflake-arctic", body=body)
    >>> for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Hello", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='chunk', data='{"chunk": "!", "created": "2023-11-28T16:32:56.724526"}')
    namespace(event='chunk', data='{"chunk": " How", "created": "2023-11-28T16:32:56.724673"}')
    namespace(event='chunk', data='{"chunk": " can", "created": "2023-11-28T16:32:56.724804"}')
    namespace(event='chunk', data='{"chunk": " I", "created": "2023-11-28T16:32:56.724941"}')
    namespace(event='chunk', data='{"chunk": " assist", "created": "2023-11-28T16:32:56.725077"}')
    namespace(event='chunk', data='{"chunk": " you", "created": "2023-11-28T16:32:56.725220"}')
    namespace(event='chunk', data='{"chunk": " today", "created": "2023-11-28T16:32:56.725354"}')
    namespace(event='chunk', data='{"chunk": "?", "created": "2023-11-28T16:32:56.725485"}')
    namespace(event='chunk', data='{"chunk": "", "created": "2023-11-28T16:32:56.725611"}')
    namespace(event='conclusion', data={'completed': True})


    >>> body = {"prompt": "A beautiful landscape", "size": "1024x1024"}
    >>> gen = call_model("dall-e", body=body)
    >>> for event in gen: print(event)
    namespace(event='attachment', data='{"attachment": "Base64 attachment", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='chunk', data='{"chunk": "![output_image.png](attachment:output_image.png)", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='conclusion', data='{"completed": true}')


    >>> body = {"prompt": {"positive_prompt": "Lion vs. Tiger", "negative_prompt": "Nudes"}, "size": "1024x1024"}
    >>> gen = call_model("stable-diffusion", body=body)
    >>> for event in gen: print(event)
    namespace(event='attachment', data='{"attachment": "Base64 attachment", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='chunk', data='{"chunk": "![output_image.png](attachment:output_image.png)", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='conclusion', data='{"completed": true}')


    >>> body = {"text_chunks": ["My father is the king"]}
    >>> gen = call_model("ada2-embedding", body=body)
    >>> for event in gen: print(event)
    namespace(event='embedding', data='{"index": "0", "embedding": "Embedding generated", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='conclusion', data={'completed': True})


    >>> body = {"audio": "Base64 encoded audio data", "language": "en"}
    >>> gen = call_model("whisperx", body=body)
    >>> for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Transcription generated", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='conclusion', data={'completed': True})

    >>> body = {"audio": "Base64 encoded audio data", "language": "en"}
    >>> gen = call_model("whisper", body=body)
    >>> for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Transcription generated", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='conclusion', data={'completed': True})


    >>> body = {"audio": "Base64 encoded audio data", "language": "en", "diarize": False}
    >>> gen = call_model("nova2", body=body)
    >>> for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Transcription generated", "created": "2023-11-28T16:32:56.724070", "paragraphs": "Transcript generated in paragraphs if diarize is True"}')
    namespace(event='conclusion', data={'completed': True})


    >>> body = {"image": "Base64 encoded image data", "features": [{"type": "DOCUMENT_TEXT_DETECTION"}]}
    >>> gen = call_model("google-vision", body=body)
    >>> for event in gen: print(event)
    namespace(event='chunk', data='{"chunk": "Image analysis generated", "created": "2023-11-28T16:32:56.724070"}')
    namespace(event='conclusion', data={'completed': True})
    """

    with httpx.Client() as httpx_client:
        with httpx_client.stream(
            **_prepare_model_request(model_name, body)
        ) as response:
            for event in parse_sse_response(response):
                if parse_data:
                    event.data = json.loads(event.data)
                yield event


def get_available_models():
    """Get the available models to call.

    Returns
    -------
    list
        A list of available models.

    Examples
    --------
    >>> models = models.get_available_models()
    >>> print(models)
    ['chat-gpt-35', 'chat-gpt-40', 'chat-gpt-40-o', 'llama3', 'snowflake-arctic', 'mixtral', 'dall-e', 'stable-diffusion', 'ada2-embedding', 'whisperx', 'google-vision', 'whisper', 'nova2']
    """
    # list of available models
    available_models = [
        "chat-gpt-35",
        "chat-gpt-40",
        "chat-gpt-40-o",
        "chat-gpt-40-o-mini",
        "llama3",
        "snowflake-arctic",
        "mixtral",
        "dall-e",
        "stable-diffusion",
        "ada2-embedding",
        "whisperx",
        "google-vision",
        "whisper",
        "nova2",
        "text2speech",
    ]

    return available_models
