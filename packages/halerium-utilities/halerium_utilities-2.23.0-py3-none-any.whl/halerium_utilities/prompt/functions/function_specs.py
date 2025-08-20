import inspect
import json
import logging

from typing import Callable, Dict, Any

from halerium_utilities.prompt.models import call_model


TEMPLATE = """
{
    "name": "<function-name>",
    "description": "<what the function does and returns>",
    "parameters": {
        "type": "object",
        "properties": { # contains zero to N parameters
            "<parameter-name>": {
                "type": "<string or number>",
                "description": "<What the parameter does>",
            }
            # possibly more parameters,  
        },
        "required": [<list of required parameters>],
    }
}
"""

SYSTEM_MSG = (
    "Your task is to generate a function schema json given a function's source code."
    "\nIn the source code the function will have a single argument which is supposed to "
    "be a dict containing the parameters. If this dict is not used anywhere in the function "
    "the parameters.properties of the schema are empty."
    "\nYour answer must be structured like this:"
    f"\n```{TEMPLATE}```\n"
    "\nANSWER ONLY WITH THE JSON STRING!"
)


RESERVED_PARAMETERS = ("path", "setup_id", "config_parameters")


def generate_json_spec_gpt(func: Callable) -> Dict[str, Any]:
    # Get the function's signature
    signature = inspect.signature(func)
    parameters = signature.parameters

    # Ensure the function has exactly one parameter and it's a pydantic BaseModel
    if len(parameters) != 1:
        raise ValueError("Function must have exactly one parameter.")

    function_source = inspect.getsource(func)

    messages = [
        {"role": "system", "content": SYSTEM_MSG},
        {"role": "user", "content": f"```\n{function_source}\n```"}
    ]
    gen = call_model("chat-gpt-40-o",
                     body={"messages": messages, "temperature": 0, "response_format": {"type": "json_object"}},
                     parse_data=True)
    answer = ""
    for event in gen:
        answer += event.data.get("chunk", "")

    to_remove = (None, "```json", "```JSON", "```")
    for tr in to_remove:
        answer = answer.strip(tr)

    json_spec = json.loads(answer)

    for r_par in RESERVED_PARAMETERS:
        if r_par in json_spec["parameters"]["properties"]:
            del json_spec["parameters"]["properties"][r_par]
            if r_par in json_spec["parameters"]["required"]:
                json_spec["parameters"]["required"].remove(r_par)
            logging.warning(f"Removing the reserved parameter {r_par} from the function schema.")

    return json_spec


def generate_json_spec_pydantic(func: Callable) -> Dict[str, Any]:
    # Check if the function has a docstring
    docstring = func.__doc__ if func.__doc__ else "No description available."

    # Get the function's signature
    signature = inspect.signature(func)
    parameters = signature.parameters

    # Ensure the function has exactly one parameter and it's a pydantic BaseModel
    if len(parameters) != 1:
        raise ValueError("Function must have exactly one parameter.")

    param_name, param = next(iter(parameters.items()))
    param_annotation = param.annotation

    try:
        # Generate JSON schema for the pydantic model
        json_schema = param_annotation.schema()
    except AttributeError:
        raise TypeError("Function's parameter must be a subclass of pydantic.BaseModel "
                        "or another object that supports the .schema() method.")

    # Modify the schema to match the desired format
    formatted_schema = {
        "type": "object",
        "properties": {
            key: {
                "type": value["type"],
                "description": value.get("description", "No description available.")
            }
            for key, value in json_schema["properties"].items()
        },
        "required": json_schema.get("required", []),
        "additionalProperties": False
    }

    # Create the JSON spec dictionary
    json_spec = {
        "name": func.__name__,
        "description": docstring,
        "parameters": formatted_schema
    }

    return json_spec

