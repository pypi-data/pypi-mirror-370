import json

from typing import Dict, List, Optional
from traceback import format_exception_only

from halerium_utilities.prompt.capabilities import (
    get_capability_groups_async,
    get_capability_group_async,
    delete_capability_group_async, 
    create_capability_group_async,
    update_capability_group_async,
    add_function_to_capability_group_async,
    delete_function_from_capability_group_async,
    update_function_in_capability_group_async
)

# Async wrapper functions for capability group management utilities and capability group function management utilities.


async def get_all_capability_groups() -> List[Dict]:
    try:
        return await get_capability_groups_async()
    except Exception as exc:
        return "".join(format_exception_only(exc))


async def get_capability_group(name: str) -> Dict:
    try:
        return await get_capability_group_async(name)
    except Exception as exc:
        return "".join(format_exception_only(exc))


async def delete_capability_group(name: str) -> Dict:
    try:
        return await delete_capability_group_async(name)
    except Exception as exc:
        return "".join(format_exception_only(exc))


async def create_capability_group(name: str,
                                  runner_type: Optional[str] = None,
                                  shared_runner: Optional[bool] = None,
                                  setup_commands: Optional[str] = None,
                                  source_code: Optional[str] = None,
                                  functions: Optional[str] = None) -> Dict:
    if setup_commands is not None:
        setup_commands = json.loads(setup_commands)
    if functions is not None:
        functions = json.loads(functions)

    try:
        return await create_capability_group_async(
            name=name,
            runner_type=runner_type,
            shared_runner=shared_runner,
            setup_commands=setup_commands,
            source_code=source_code,
            functions=functions)
    except Exception as exc:
        return "".join(format_exception_only(exc))


async def update_capability_group(name: str,
                                  new_name: Optional[str] = None,
                                  runner_type: Optional[str] = None,
                                  shared_runner: Optional[bool] = None,
                                  setup_commands: Optional[str] = None,
                                  source_code: Optional[str] = None,
                                  functions: Optional[str] = None) -> Dict:
    if setup_commands is not None:
        setup_commands = json.loads(setup_commands)
    if functions is not None:
        functions = json.loads(functions)

    try:
        await update_capability_group_async(
            name=name, new_name=new_name,
            runner_type=runner_type,
            shared_runner=shared_runner,
            setup_commands=setup_commands,
            source_code=source_code,
            functions=functions)
        return "Update successful"
    except Exception as exc:
        return "".join(format_exception_only(exc))


async def add_function_to_group(name: str,
                                source_code: Optional[str] = None,
                                function: Optional[str] = None) -> Dict:
    if function is not None:
        function = json.loads(function)
    
    try:
        await add_function_to_capability_group_async(name, source_code, function)
        return "Update successful"
    except Exception as exc:
        return "".join(format_exception_only(exc))


async def delete_function_from_group(name: str, function: str) -> Dict:
    try:
        await delete_function_from_capability_group_async(name, function)
        return "Update successful"
    except Exception as exc:
        return "".join(format_exception_only(exc))


async def update_function_in_group(name: str,
                                   old_function_name: str,
                                   source_code: Optional[str] = None,
                                   new_function: Optional[str] = None) -> Dict:
    if new_function is not None:
        new_function = json.loads(new_function)
    
    try:
        await update_function_in_capability_group_async(
            name, 
            old_function_name, 
            source_code, 
            new_function
        )
        return "Update successful"
    except Exception as exc:
        return "".join(format_exception_only(exc))
