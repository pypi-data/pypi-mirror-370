import httpx
import importlib
import os
import uuid
import sys

from pathlib import Path
from typing import Union

from . import function_specs as specs


TIMEOUT = 20


def prepare_register(file_path: Union[str, Path], function: str,
                     function_name: str = None, function_schema: dict = None,
                     config_parameters: dict = None,
                     group: str = None, pretty_name: str = None,
                     allow_gpt=True) -> dict:

    file_path = str(Path(file_path).resolve())

    # remember modules
    prior_modules = {**sys.modules}

    unique_module_name = f"dynamic_module_{uuid.uuid5(uuid.NAMESPACE_URL, file_path)}"
    unique_module_name = unique_module_name.replace("-", "_")

    # Import the module dynamically
    # 1. store original working directory
    original_cwd = os.getcwd()
    try:
        # 2. change working directory to that of the file
        os.chdir(os.path.dirname(file_path))
        # 3. do the import
        spec = importlib.util.spec_from_file_location(unique_module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        # 4. restore original working directory
        os.chdir(original_cwd)

    if not hasattr(module, function):
        raise AttributeError(f"File {file_path} does not contain a function {function}.")

    func_obj = getattr(module, function)

    if function_schema:
        function_spec = function_schema
    else:
        try:
            function_spec = specs.generate_json_spec_pydantic(func_obj)
        except (TypeError, KeyError) as exc:
            if allow_gpt:
                function_spec = specs.generate_json_spec_gpt(func_obj)
            else:
                raise exc

    if function_name:
        function_spec["name"] = function_name

    # cleanup
    del module
    del spec
    del func_obj
    for key in list(sys.modules):
        if key not in prior_modules:
            del sys.modules[key]
    # cleanup done

    body = {"file_path": file_path,
            "function": function,
            "function_spec": function_spec,
            "group": group,
            "pretty_name": pretty_name,
            }
    if config_parameters:
        body["config_parameters"] = config_parameters

    return body


def register_function(file_path: Union[str, Path], function: str,
                      function_name: str = None, function_schema: dict = None,
                      config_parameters: dict = None, group: str = None,
                      pretty_name: str = None):
    """
    Registers a function with the custom function service so that
    it can be used by bots that are connected to the Halerium runner.
    The function must accept a single argument of type dict which
    then contains the actual parameters.

    The functions will be executed in the home directory `/home/jovyan/`

    Parameters
    ----------
    file_path (str or Path):
        the path of the source .py file in which the function is located
    function (str):
        the object name of the function
    function_name (str, optional):
        the name under which to register the function. If not set it will
        be set to the object name `function`.
    function_schema (dict, optional):
        the schema of the function. If not set this method will attempt
        to infer the schema automatically from the functions docstring
        and a pydantic Model based annotation of the function argument
        or by analyzing the functions source code with GPT-4o.
    config_parameters (dict, optional):
        possible fixed parameters to the function on each call.
        Must be JSON serializable.
        These parameter will be inserted into the function argument
        dict under the key config_parameters.
    group (str, optional):
        group name for the function. Functions with the same
        group name will be displayed together. Functions with no group
        name will appear in the "Custom Functions" group.
    pretty_name (str, optional):
        display name for the function. Will be user as a display name
        in the bot setup card and within the function call.
        If no pretty_name is provided function_name will be used
        for display.

    Returns
    -------
    dict: the result (status, error, ...) of the registration attempt

    Function Schema Example
    -----------------------
    ```
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
    ```
    """
    body = prepare_register(
        file_path=file_path,
        function_name=function_name,
        function=function,
        function_schema=function_schema,
        config_parameters=config_parameters,
        group=group,
        pretty_name=pretty_name,
    )

    response = httpx.post("http://0.0.0.0:8800/register_function",
                          json=body,
                          timeout=TIMEOUT)

    return response.json()


async def register_function_async(file_path: Union[str, Path], function: str,
                                  function_name: str = None, function_schema: dict = None,
                                  config_parameters: dict = None, group: str = None,
                                  pretty_name: str = None):
    """
    Asynchronously registers a function with the custom function service so that
    it can be used by bots that are connected to the Halerium runner.
    The function must accept a single argument of type dict which
    then contains the actual parameters.

    The functions will be executed in the home directory `/home/jovyan/`

    Parameters
    ----------
    file_path (str or Path):
        the path of the source .py file in which the function is located
    function (str):
        the object name of the function
    function_name (str, optional):
        the name under which to register the function. If not set it will
        be set to the object name `function`.
    function_schema (dict, optional):
        the schema of the function. If not set this method will attempt
        to infer the schema automatically from the functions docstring
        and a pydantic Model based annotation of the function argument
        or by analyzing the functions source code with GPT-4o.
    config_parameters (dict, optional):
        possible fixed parameters to the function on each call.
        Must be JSON serializable.
        These parameter will be inserted into the function argument
        dict under the key config_parameters.
    group (str, optional):
        group name for the function. Functions with the same
        group name will be displayed together. Functions with no group
        name will appear in the "Custom Functions" group.
    pretty_name (str, optional):
        display name for the function. Will be user as a display name
        in the bot setup card and within the function call.
        If no pretty_name is provided function_name will be used
        for display.

    Returns
    -------
    dict: the result (status, error, ...) of the registration attempt

    Function Schema Example
    -----------------------
    ```
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
    ```
    """
    body = prepare_register(
        file_path=file_path,
        function_name=function_name,
        function=function,
        function_schema=function_schema,
        config_parameters=config_parameters,
        group=group,
        pretty_name=pretty_name,
    )

    async with httpx.AsyncClient() as client:
        response = await client.post("http://0.0.0.0:8800/register_function",
                                     json=body,
                                     timeout=TIMEOUT)

    return response.json()


def unregister_function(function_name: str):
    """
    Asynchronously unregisters a function with the custom function service of
    Halerium runner.

    Parameters
    ----------
    function_name (str): the name of the function.

    Returns
    -------
    dict: the result (status, error, ...) of the unregistration attempt
    """
    response = httpx.post("http://0.0.0.0:8800/unregister_function",
                          json={"function_name": function_name},
                          timeout=TIMEOUT)
    return response.json()


async def unregister_function_async(function_name: str):
    """
    Unregisters a function with the custom function service of
    Halerium runner.

    Parameters
    ----------
    function_name (str): the name of the function.

    Returns
    -------
    dict: the result (status, error, ...) of the unregistration attempt
    """
    async with httpx.AsyncClient() as client:
        response = await client.post("http://0.0.0.0:8800/unregister_function",
                                     json={"function_name": function_name},
                                     timeout=TIMEOUT)
    return response.json()


def restart_custom_function_service():
    """
    Restarts the custom function service.
    This results in all registered functions to be unloaded.

    Returns
    -------
    dict: the result (status, error, ...) of the restart attempt
    """
    response = httpx.post("http://0.0.0.0:8800/control_custom_service",
                          json={"action": "restart"},
                          timeout=TIMEOUT)
    return response.json()


async def restart_custom_function_service_async():
    """
    Restarts the custom function service.
    This results in all registered functions to be unloaded.

    Returns
    -------
    dict: the result (status, error, ...) of the restart attempt
    """
    async with httpx.AsyncClient() as client:
        response = await client.post("http://0.0.0.0:8800/control_custom_service",
                                     json={"action": "restart"},
                                     timeout=TIMEOUT)
    return response.json()
