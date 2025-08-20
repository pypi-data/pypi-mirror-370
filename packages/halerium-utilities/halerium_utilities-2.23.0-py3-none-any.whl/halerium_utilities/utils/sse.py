import httpx
from types import SimpleNamespace


async def parse_sse_response_async(response: httpx.Response):
    response.raise_for_status()
    event = dict(event=None, data=None)
    async for line in response.aiter_lines():
        finished_event = process_line(line, event)
        if finished_event:
            yield SimpleNamespace(**event)
            event = dict(event=None, data=None)

    if event["data"] is not None or event["event"] is not None:
        yield SimpleNamespace(**event)


def parse_sse_response(response: httpx.Response):
    response.raise_for_status()
    event = dict(event=None, data=None)
    for line in response.iter_lines():
        finished_event = process_line(line, event)
        if finished_event:
            yield SimpleNamespace(**event)
            event = dict(event=None, data=None)

    if event["data"] is not None or event["event"] is not None:
        yield SimpleNamespace(**event)


def process_line(line, event):
    line = line.strip()
    if not line:
        if event["data"]:
            return True
    else:
        field, value = line.split(":", 1)
        field = field.strip()
        value = value.strip()
        if field == "event":
            event["event"] = value
        elif field == "data":
            if event["data"] is not None:
                event["data"] += "\n" + value
            else:
                event["data"] = value

    return False
