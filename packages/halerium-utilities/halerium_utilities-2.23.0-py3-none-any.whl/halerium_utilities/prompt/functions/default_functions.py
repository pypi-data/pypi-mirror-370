from pathlib import Path

from halerium_utilities.prompt.functions.custom_service import prepare_register


REGISTRY = {
    # "my_function": {  # name of the function
    #     "file": "my_function.py",
    #     "function": "func",  # what it says after `def:`
    # }
    "get_docx_placeholders": {
        "file_path": "docx_templates.py",
        "function": "get_docx_placeholders",
        "group": "Document functions",
        "pretty_name": "Get DOCX placeholders",
    },
    "fill_docx_template": {
        "file_path": "docx_templates.py",
        "function": "fill_docx_template",
        "group": "Document functions",
        "pretty_name": "Fill DOCX template",
    },
    "get_pptx_placeholders": {
        "file_path": "pptx_templates.py",
        "function": "get_pptx_placeholders",
        "group": "Document functions",
        "pretty_name": "Get PPTX placeholders",
    },
    "fill_pptx_template": {
        "file_path": "pptx_templates.py",
        "function": "fill_pptx_template",
        "group": "Document functions",
        "pretty_name": "Fill PPTX template",
    },
    "load_website": {
        "file_path": "web_crawler_functions.py",
        "function": "load_website",
        "group": "Web functions",
        "pretty_name": "Load website",
    },
    "get_subagents": {
        "file_path": "subagent_functions.py",
        "function": "get_subagents",
        "group": "Subagent functions",
        "pretty_name": "Get subagents",
    },
    "execute_subagent": {
        "file_path": "subagent_functions.py",
        "function": "execute_subagent",
        "group": "Subagent functions",
        "pretty_name": "Execute subagent",
    },
}


def get_full_registry():
    full_registry = {}
    for function_name, params in REGISTRY.items():
        try:
            file_path = Path(__file__).parent.resolve() / "library" / params["file_path"]
            function = params["function"]
            group = params.get("group")
            pretty_name = params.get("pretty_name")
            full_spec = prepare_register(file_path=file_path, function=function, function_name=function_name,
                                         group=group, pretty_name=pretty_name, allow_gpt=False)
            full_registry[function_name] = full_spec
        except:
            pass
    return full_registry

