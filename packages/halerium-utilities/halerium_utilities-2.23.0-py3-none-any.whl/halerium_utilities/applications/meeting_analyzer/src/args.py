class CLIArgs:
    args = {
        "CHATBOTPORT": {
            "name_or_flags": ["-c", "--cbport"],
            "type": int,
            "help": "Port under which to find the corresponding chatbot.",
            "required": True,
        },
        "LOGGERLEVEL": {
            "name_or_flags": ["-l", "--logger_level"],
            "type": int,
            "help": "Logger level: 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL.",
            "required": False,
            "default": 20,
        },
        "MEETINGSPATH": {
            "name_or_flags": ["-m", "--meetings_path"],
            "type": str,
            "help": "Path to the folder in which the meeting analyses are stored.",
            "required": False,
            "default": "./meetings",
        },
        "PORT": {
            "name_or_flags": ["-o", "--port"],
            "type": int,
            "help": "Port to start API on. Defaults to 8501.",
            "required": False,
        },
        "TEMPLATE": {
            "name_or_flags": ["-b", "--board"],
            "type": str,
            "help": "Path to the analyzer template board.",
            "required": True,
        },
        "UPLOADPATH": {
            "name_or_flags": ["-u", "--upload_path"],
            "type": str,
            "help": "Path to the folder in which uploaded audio files are stored.",
            "required": False,
            "default": "./uploads",
        },
    }
