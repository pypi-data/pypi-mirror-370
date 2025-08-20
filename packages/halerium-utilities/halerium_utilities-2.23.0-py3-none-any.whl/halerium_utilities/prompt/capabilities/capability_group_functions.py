from typing import Dict, Optional
import os
import ast

from .schemas import ParametersModel, FunctionModel

from .capabilities import get_capability_group, update_capability_group, get_capability_group_async, update_capability_group_async


def _get_source_code(name: str) -> str:
    """
    Retrieves the source code for a given capability group.

    Parameters
    ----------
    name (str): The name of the capability group.

    Returns
    -------
    str: The source code of the capability group.
    """
    
    # Get the existing source code
    existing_source_path = os.path.join("/home/jovyan", ".functions", name, "source.py")
    
    if os.path.exists(existing_source_path):
        with open(existing_source_path, "r") as f:
            return f.read()
    return ""


def add_function_to_capability_group(name: str, 
                                     source_code: Optional[str] = None,
                                     function: Optional[Dict] = None) -> Dict:
    """
    Adds a function to an existing capability group.

    Parameters
    ----------
    name (str): the name of the capability group.
    source_code (str, optional): The source code of the function.
    function (Dict, optional): Function to add to the capability group.

    Returns
    -------
    dict: the result (status, error, ...) of the update attempt.
    """

    # Get the existing capability group details
    capability_group = get_capability_group(name)

    # get existing source code and update it with new source code
    existing_source_code = _get_source_code(name)
    
    updated_source_code = existing_source_code + ("\n" + source_code if source_code else "")

    # get existing functions
    existing_functions = capability_group["functions"]

    new_function = FunctionModel(
        function=function["function"],
        pretty_name=function["pretty_name"],
        description=function["description"],
        config_parameters=function["config_parameters"],
        parameters=ParametersModel(
            properties=function["parameters"]["properties"],
            required=function["parameters"]["required"]
        )
    ) if function else None
    
    # Append the new function to the list if provided
    functions = existing_functions + ([new_function.dict()] if function else [])

    # Update the capability group with the new function
    update_result = update_capability_group(
        name=name,
        source_code=updated_source_code,
        functions=functions
    )

    return update_result


async def add_function_to_capability_group_async(name: str, 
                                                 source_code: Optional[str] = None,
                                                 function: Optional[Dict] = None) -> Dict:
    """
    Asynchronously adds a function to an existing capability group.

    Parameters
    ----------
    name (str): the name of the capability group.
    source_code (str, optional): The source code of the function.
    function (Dict, optional): Function to add to the capability group.

    Returns
    -------
    dict: the result (status, error, ...) of the update attempt.
    """
    # Get the existing capability group details
    capability_group = await get_capability_group_async(name)

    # get existing source code and update it with new source code
    existing_source_code = _get_source_code(name)
    
    updated_source_code = existing_source_code + ("\n" + source_code if source_code else "")

    # get existing functions
    existing_functions = capability_group["functions"]

    new_function = FunctionModel(
        function=function["function"],
        pretty_name=function["pretty_name"],
        description=function["description"],
        config_parameters=function["config_parameters"],
        parameters=ParametersModel(
            properties=function["parameters"]["properties"],
            required=function["parameters"]["required"]
        )
    ) if function else None
    
    # Append the new function to the list if provided
    functions = existing_functions + ([new_function.dict()] if function else [])

    # Update the capability group with the new function
    update_result = await update_capability_group_async(
        name=name,
        source_code=updated_source_code,
        functions=functions
    )

    return update_result


def _remove_function_source_code(source_code: str, function_name: str) -> str:
    """
    Removes the source code of a specified function and its preceding import statements
    from the given source code using AST and line tracking.

    Parameters
    ----------
    source_code (str): the original source code.
    function_name (str): the name of the function to be removed.

    Returns
    -------
    str: the updated source code with the specified function and relevant imports removed.
    """
    # Split the source code into lines for manual line tracking
    lines = source_code.splitlines()

    # Parse the source code into an AST
    try:
        tree = ast.parse(source_code)
    except Exception:
        # If parsing or manipulation fails, return the original source code
        return source_code

    # Step 1: Locate the target function and its line range
    target_func = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            target_func = node
            break

    # If function not found, return the source unchanged
    if not target_func:
        return source_code.strip()

    func_start = target_func.lineno - 1  # convert to 0-based index
    func_end = target_func.end_lineno - 1

    # Step 2: Identify all contiguous import lines directly before the function
    import_lines = set()
    i = func_start - 1
    while i >= 0:
        stripped = lines[i].strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            import_lines.add(i)
            i -= 1
        elif stripped == "":
            i -= 1  # allow empty lines in between
        else:
            break  # stop at any non-import, non-empty line

    # Step 3: Mark all lines of the function for removal
    func_lines = set(range(func_start, func_end + 1))

    # Combine import and function lines to be removed
    lines_to_remove = func_lines.union(import_lines)

    # Step 4: Rebuild the source code excluding those lines
    new_lines = [line for idx, line in enumerate(lines) if idx not in lines_to_remove]

    return "\n".join(new_lines).strip()


def delete_function_from_capability_group(name: str, function: str) -> Dict:
    """
    Deletes a function from an existing capability group.

    Parameters
    ----------
    name (str): the name of the capability group.
    function (str): the object name of the function to be deleted.

    Returns
    -------
    dict: the result (status, error, ...) of the update attempt.
    """
    # Get the existing capability group details
    capability_group = get_capability_group(name)

    # Check if the function exists in the capability group
    existing_functions = capability_group["functions"]
    if not any(func["function"] == function for func in existing_functions):
        return {"error": f"Function {function} not found in capability group {name}."}
    
    # get existing source code
    existing_source_code = _get_source_code(name)

    # Remove the function's source code from the existing source code using AST
    updated_source_code = _remove_function_source_code(existing_source_code, function)

    # Remove the specified function from the list of existing functions
    updated_functions = [func for func in existing_functions if func["function"] != function]

    # Update the capability group with the updated functions and source code
    update_result = update_capability_group(
        name=name,
        source_code=updated_source_code,
        functions=updated_functions
    )

    return update_result


async def delete_function_from_capability_group_async(name: str, function: str) -> Dict:
    """
    Asynchronously deletes a function from an existing capability group.

    Parameters
    ----------
    name (str): the name of the capability group.
    function (str): the object name of the function to be deleted.

    Returns
    -------
    dict: the result (status, error, ...) of the update attempt.
    """
    # Get the existing capability group details
    capability_group = await get_capability_group_async(name)

    # Check if the function exists in the capability group
    existing_functions = capability_group["functions"]
    if not any(func["function"] == function for func in existing_functions):
        return {"error": f"Function {function} not found in capability group {name}."}
    
    # get existing source code
    existing_source_code = _get_source_code(name)

    # Remove the function's source code from the existing source code using AST
    updated_source_code = _remove_function_source_code(existing_source_code, function)

    # Remove the specified function from the list of existing functions
    updated_functions = [func for func in existing_functions if func["function"] != function]

    # Update the capability group with the updated functions and source code
    update_result = await update_capability_group_async(
        name=name,
        source_code=updated_source_code,
        functions=updated_functions
    )

    return update_result


def update_function_in_capability_group(name: str, 
                                        old_function_name: str,
                                        source_code: Optional[str] = None,
                                        new_function: Optional[Dict] = None) -> Dict:
    """
    Updates a function in an existing capability group.

    Parameters
    ----------
    name (str): the name of the capability group.
    old_function_name (str): the object name of the function to be updated.
    source_code (str, optional): the source code of the updated function.
    new_function (Dict, optional): the new function details.

    Returns
    -------
    dict: the result (status, error, ...) of the update attempt.
    """
    # Get the existing capability group details
    capability_group = get_capability_group(name)

    # Get existing functions and find the specified function
    existing_functions = capability_group["functions"]
    function_to_update = None
    for func in existing_functions:
        if func["function"] == old_function_name:
            function_to_update = func
            break

    if not function_to_update:
        return {"error": f"Function {old_function_name} not found in capability group {name}."}

    # Delete the existing function
    delete_result = delete_function_from_capability_group(name, old_function_name)
    if "error" in delete_result:
        return delete_result

    # Add the updated function
    update_function_result = add_function_to_capability_group(
        name=name,
        source_code=source_code,
        function=new_function if new_function else function_to_update
    )

    return update_function_result


async def update_function_in_capability_group_async(name: str,
                                                  old_function_name: str,
                                                  source_code: Optional[str] = None,
                                                  new_function: Optional[Dict] = None) -> Dict:
    """
    Asynchronously updates a function in an existing capability group.

    Parameters
    ----------
    name (str): the name of the capability group.
    old_function_name (str): the object name of the function to be updated.
    source_code (str, optional): the source code of the updated function.
    new_function (Dict, optional): the new function details.

    Returns
    -------
    dict: the result (status, error, ...) of the update attempt.
    """
    # Get the existing capability group details
    capability_group = await get_capability_group_async(name)

    # Get existing functions and find the specified function
    existing_functions = capability_group["functions"]
    function_to_update = None
    for func in existing_functions:
        if func["function"] == old_function_name:
            function_to_update = func
            break

    if not function_to_update:
        return {"error": f"Function {old_function_name} not found in capability group {name}."}

    # Delete the existing function
    delete_result = await delete_function_from_capability_group_async(name, old_function_name)
    if "error" in delete_result:
        return delete_result

    # Add the updated function
    update_function_result = await add_function_to_capability_group_async(
        name=name,
        source_code=source_code,
        function=new_function if new_function else function_to_update
    )

    return update_function_result

