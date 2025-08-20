from halerium_utilities.board.connection_rules.connectors import CONNECTORS


NODE_CONNECTORS = {
    "note": [
        CONNECTORS["note-top"],
        CONNECTORS["note-bottom"],
        CONNECTORS["note-left"],
        CONNECTORS["note-right"],
    ],
    "setup": [
        CONNECTORS["context-input"],
        CONNECTORS["prompt-output"]
    ],
    "bot": [
        CONNECTORS["context-input"],
        CONNECTORS["context-output"],
        CONNECTORS["prompt-input"],
        CONNECTORS["prompt-output"]
    ],
    "frame": [
        CONNECTORS["frame-top"],
        CONNECTORS["frame-bottom"],
        CONNECTORS["frame-left"],
        CONNECTORS["frame-right"],
    ]
}
