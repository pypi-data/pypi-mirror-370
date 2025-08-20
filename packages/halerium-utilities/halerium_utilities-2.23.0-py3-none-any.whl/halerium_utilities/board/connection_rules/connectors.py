

class Connector:
    name = None
    source_to = []
    target_to = []


class NoteTopConnector(Connector):
    name = "note-top"
    source_to = [
        {"type": "solid_arrow", "amount": -1},
    ]
    target_to = [
        {"type": "dashed_line", "amount": -1},
        {"type": "solid_arrow", "amount": -1},
    ]


class NoteBottomConnector(Connector):
    name = "note-bottom"
    source_to = [
        {"type": "dashed_line", "amount": -1},
        {"type": "solid_arrow", "amount": -1},
    ]
    target_to = [
        {"type": "solid_arrow", "amount": -1},
    ]


class NoteLeftConnector(Connector):
    name = "note-left"
    source_to = [
        {"type": "solid_arrow", "amount": -1},
    ]
    target_to = [
        {"type": "solid_arrow", "amount": -1},
    ]


class NoteRightConnector(Connector):
    name = "note-right"
    source_to = [
        {"type": "solid_arrow", "amount": -1},
    ]
    target_to = [
        {"type": "solid_arrow", "amount": -1},
    ]


class PromptInputConnector(Connector):
    name = "prompt-input"
    target_to = [
        {"type": "prompt_line", "amount": 1},
    ]


class PromptOutputConnector(Connector):
    name = "prompt-output"
    source_to = [
        {"type": "prompt_line", "amount": -1},
    ]


class ContextInputConnector(Connector):
    name = "context-input"
    target_to = [
        {"type": "solid_arrow", "amount": -1},
    ]


class ContextOutputConnector(Connector):
    name = "context-output"
    source_to = [
        {"type": "solid_arrow", "amount": -1},
    ]


class FrameTopConnector(Connector):
    name = "frame-top"
    source_to = [
        {"type": "solid_arrow", "amount": -1},
    ]


class FrameBottomConnector(Connector):
    name = "frame-bottom"
    source_to = [
        {"type": "solid_arrow", "amount": -1},
    ]


class FrameLeftConnector(Connector):
    name = "frame-left"
    source_to = [
        {"type": "solid_arrow", "amount": -1},
    ]


class FrameRightConnector(Connector):
    name = "frame-right"
    source_to = [
        {"type": "solid_arrow", "amount": -1},
    ]


CONNECTORS = {NoteTopConnector.name: NoteTopConnector,
              NoteBottomConnector.name: NoteBottomConnector,
              NoteLeftConnector.name: NoteLeftConnector,
              NoteRightConnector.name: NoteRightConnector,
              PromptInputConnector.name: PromptInputConnector,
              PromptOutputConnector.name: PromptOutputConnector,
              ContextInputConnector.name: ContextInputConnector,
              ContextOutputConnector.name: ContextOutputConnector,
              FrameTopConnector.name: FrameTopConnector,
              FrameBottomConnector.name: FrameBottomConnector,
              FrameLeftConnector.name: FrameLeftConnector,
              FrameRightConnector.name: FrameRightConnector,}
