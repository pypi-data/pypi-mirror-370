import httpx
import os

from typing import Dict, List, Optional

from .schemas import CapabilityGroupModel, FunctionModel, UpdateCapabilityGroupModel


class CapabilityGroupException(Exception):
    pass


TIMEOUT = 20


def _get_base_endpoint_url() -> str:
    """
    Constructs the base endpoint URL using environment variables.

    Returns
    -------
    str
        The base endpoint URL.
    """
    base_url = os.environ['HALERIUM_BASE_URL']
    tenant = os.environ['HALERIUM_TENANT_KEY']
    workspace = os.environ['HALERIUM_PROJECT_ID']
    return f"{base_url}/api/tenants/{tenant}/projects/{workspace}/runners/{os.environ['HALERIUM_ID']}/token-access"


def _get_headers() -> dict:
    """
    Constructs the headers for HTTP requests.

    Returns
    -------
    dict
        The headers for HTTP requests.
    """
    return {"Content-Type": "application/json",
            "halerium-runner-token": os.environ["HALERIUM_TOKEN"]}


def _get_capability_groups() -> List[Dict]:
    endpoint = _get_base_endpoint_url() + "/manifests"
    response = httpx.get(endpoint, headers=_get_headers())
    response.raise_for_status()

    return response.json().get("data", [])


async def _get_capability_groups_async() -> List[Dict]:
    """
    Asynchronously retrieves a list of capability groups.

    Returns
    -------
    List[Dict]
        A list of capability groups.
    """
    endpoint = _get_base_endpoint_url() + "/manifests"
    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, headers=_get_headers())
        response.raise_for_status()
        return response.json().get("data", [])


def _transform_capability_groups_data(raw_data):
    relevant_data = []
    for capa_group in raw_data:
        relevant_data.append({
            "name": capa_group["name"],
            "editable": not capa_group["global"],
            "functions": [
                {"name": f["function"]["name"],
                 "description": f["function"]["description"]}
                for f in capa_group["runnerFunctions"]
            ]
        })

    return relevant_data


def get_capability_groups() -> List[Dict]:
    """
    Retrieves the list of capability groups.

    Returns
    -------
    List[Dict]
        List of capability groups.
    """

    raw_data = _get_capability_groups()

    return _transform_capability_groups_data(raw_data)


async def get_capability_groups_async() -> List[Dict]:
    """
    Asynchronously retrieves the list of capability groups.

    Returns
    -------
    List[Dict]
        List of capability groups.
    """

    raw_data = await _get_capability_groups_async()

    return _transform_capability_groups_data(raw_data)


def _transform_capability_group_data(capability_group_data):
    source_path = os.path.join("/home/jovyan", ".functions", capability_group_data.get("name", ""), "source.py")
    if os.path.exists(source_path):
        with open(source_path, "r") as f:
            source_code = f.read()
    else:
        source_code = None

    capability_group_data["sourceCode"] = source_code
    # Validate the capability group against the CapabilityGroupModel
    capability_group = CapabilityGroupModel.validate(capability_group_data)
    return capability_group.dict()


def get_capability_group(name: str) -> Dict:
    """
    Retrieves details of a specific capability group by name.

    Parameters
    ----------
    name : str
        The name of the capability group.

    Returns
    -------
    Dict
        The details of the capability group.
    """
    capability_group_id = _get_capability_id_by_name(name)
    endpoint = _get_base_endpoint_url() + f"/manifests/{capability_group_id}"

    response = httpx.get(endpoint, headers=_get_headers())
    response.raise_for_status()
    capability_group_data = response.json().get("data", {})

    return _transform_capability_group_data(capability_group_data)


async def get_capability_group_async(name: str) -> Dict:
    """
    Asynchronously retrieves details of a specific capability group by name.

    Parameters
    ----------
    name : str
        The name of the capability group.

    Returns
    -------
    Dict
        The details of the capability group.
    """
    capability_group_id = await _get_capability_id_by_name_async(name)
    endpoint = _get_base_endpoint_url() + f"/manifests/{capability_group_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, headers=_get_headers())
        response.raise_for_status()
        capability_group_data = response.json().get("data", {})

    return _transform_capability_group_data(capability_group_data)


def _get_capability_id_by_name(name: str) -> Dict:
    """
    Retrieves the ID of a capability group by name.

    Parameters
    ----------
    name : str
        The name of the capability group.

    Returns
    -------
    Dict
        The ID of the capability group.
    """
    capability_groups = _get_capability_groups()

    for capability_group in capability_groups:
        if capability_group.get("name") == name:
            return capability_group.get("id")
    raise CapabilityGroupException(f"Capability group {name} not found.")


async def _get_capability_id_by_name_async(name: str) -> Dict:
    """
    Asynchronously retrieves the ID of a capability group by name.

    Parameters
    ----------
    name : str
        The name of the capability group.

    Returns
    -------
    Dict
        The ID of the capability group.
    """
    capability_groups = await _get_capability_groups_async()

    for capability_group in capability_groups:
        if capability_group.get("name") == name:
            return capability_group.get("id")
    raise CapabilityGroupException(f"Capability group {name} not found.")


def delete_capability_group(name: str) -> Dict:
    """
    Deletes a capability group by name.

    Parameters
    ----------
    name : str
        The name of the capability group.

    Returns
    -------
    Dict
        The result of the deletion operation.
    """
    capability_group_id = _get_capability_id_by_name(name)

    endpoint = _get_base_endpoint_url() + f"/manifests/{capability_group_id}"

    response = httpx.delete(endpoint, headers=_get_headers())
    response.raise_for_status()
    return response.json().get("data", {})


async def delete_capability_group_async(name: str) -> Dict:
    """
    Asynchronously deletes a capability group by name.

    Parameters
    ----------
    name : str
        The name of the capability group.

    Returns
    -------
    Dict
        The result of the deletion operation.
    """
    capability_group_id = await _get_capability_id_by_name_async(name)

    endpoint = _get_base_endpoint_url() + f"/manifests/{capability_group_id}"

    async with httpx.AsyncClient() as client:
        response = await client.delete(endpoint, headers=_get_headers())
        response.raise_for_status()
        return response.json().get("data", {})


def create_capability_group(name: str,
                            runner_type: str = None,
                            shared_runner: bool = None,
                            setup_commands: List[str] = None,
                            source_code: str = None,
                            functions: Optional[List[Dict]] = None) -> Dict:
    """
    Creates a new capability group.

    Parameters
    ----------
    name : str
        The name of the capability group.
    runner_type : Optional[str], optional
        The type of runner, by default None.
    shared_runner : Optional[bool], optional
        Whether the runner is shared, by default None.
    setup_commands : Optional[List[str]], optional
        The setup commands, by default None.
    source_code : Optional[str], optional
        The source code, by default None.
    functions : Optional[List[Dict]], optional
        The functions, by default None.

    Returns
    -------
    Dict
        The result of the creation operation.
    """
    if not setup_commands:
        setup_commands = []

    # Validate the name
    if not name:
        raise ValueError("Name is required.")
    if "\n" in name:
        raise ValueError("Name cannot contain line breaks.")

    runner_type = runner_type if runner_type else "nano"
    shared_runner = bool(shared_runner)
    setup_commands = [str(c) for c in setup_commands] if setup_commands else []
    source_code = str(source_code) if source_code else ""
    functions = [FunctionModel.validate({**func, "group": name}).dict() for func in functions] if functions else []

    payload = {
        "name": name,
        "displayName": name,
        "runnerType": runner_type,
        "sharedRunner": shared_runner,
        'setupCommand': {'setupCommands': setup_commands},
        "sourceCode": source_code,
        "functions": functions
    }

    # Validate payload
    payload = CapabilityGroupModel.validate(payload).dict()

    endpoint = _get_base_endpoint_url() + "/manifests"

    # Make the POST request
    response = httpx.post(
        endpoint,
        json=payload,
        headers=_get_headers()
    )
    try:
        response.raise_for_status()
        capability_group_data = response.json().get("data", {})
        return _transform_capability_group_data(capability_group_data)
    except httpx.HTTPStatusError:
        return response.json()


async def create_capability_group_async(name: str,
                                        runner_type: str = None,
                                        shared_runner: bool = None,
                                        setup_commands: List[str] = None,
                                        source_code: str = None,
                                        functions: Optional[List[Dict]] = None) -> Dict:
    """
    Asynchronously creates a new capability group.

    Parameters
    ----------
    name : str
        The name of the capability group.
    runner_type : Optional[str], optional
        The type of runner, by default None.
    shared_runner : Optional[bool], optional
        Whether the runner is shared, by default None.
    setup_commands : Optional[List[str]], optional
        The setup commands, by default None.
    source_code : Optional[str], optional
        The source code, by default None.
    functions : Optional[List[Dict]], optional
        The functions, by default None.

    Returns
    -------
    Dict
        The result of the creation operation.
    """
    if not setup_commands:
        setup_commands = []

    # Validate the name
    if not name:
        raise ValueError("Name is required.")
    if "\n" in name:
        raise ValueError("Name cannot contain line breaks.")

    runner_type = runner_type if runner_type else "nano"
    shared_runner = bool(shared_runner)
    setup_commands = [str(c) for c in setup_commands] if setup_commands else []
    source_code = str(source_code) if source_code else ""
    functions = [FunctionModel.validate({**func, "group": name}).dict() for func in functions] if functions else []

    payload = {
        "name": name,
        "displayName": name,
        "runnerType": runner_type,
        "sharedRunner": shared_runner,
        'setupCommand': {'setupCommands': setup_commands},
        "sourceCode": source_code,
        "functions": functions
    }

    # Validate payload
    payload = CapabilityGroupModel.validate(payload).dict()

    endpoint = _get_base_endpoint_url() + "/manifests"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json=payload,
            headers=_get_headers()
        )
        try:
            response.raise_for_status()
            capability_group_data = response.json().get("data", {})
            return _transform_capability_group_data(capability_group_data)
        except httpx.HTTPStatusError:
            return response.json()


def update_capability_group(name: str,
                            new_name: Optional[str] = None,
                            runner_type: Optional[str] = None,
                            shared_runner: Optional[bool] = None,
                            setup_commands: Optional[List[str]] = None,
                            source_code: Optional[str] = None,
                            functions: Optional[List[Dict]] = None) -> Dict:
    """
    Updates an existing capability group.

    Parameters
    ----------
    name : str
        The current name of the capability group.
    new_name : Optional[str], optional
        The new name of capability group to update to, by default None.
    runner_type : Optional[str], optional
        The type of runner, by default None.
    shared_runner : Optional[bool], optional
        Whether the runner is shared, by default None.
    setup_commands : Optional[List[str]], optional
        The setup commands, by default None.
    source_code : Optional[str], optional
        The source code, by default None.
    functions : Optional[List[Dict]], optional
        The functions, by default None.

    Returns
    -------
    Dict
        The result of the update operation.
    """
    capability_id = _get_capability_id_by_name(name)

    endpoint = _get_base_endpoint_url() + f"/manifests/{capability_id}"

    if functions is not None:
        functions = [FunctionModel.validate({**func, "group": name}).dict() for func in functions]

    if setup_commands is None:
        setup_command = None
    else:
        setup_command = {"setupCommands": setup_commands}

    # fixes loss of source code on rename
    if new_name and source_code is None:
        # fetch source code in the case of name change to not lose reference
        source_path = os.path.join("/home/jovyan", ".functions", name, "source.py")

        if os.path.exists(source_path):
            with open(source_path, "r") as f:
                source_code = f.read()
        else:
            source_code = None

    # Validate payload and exclude None values
    capability_group = UpdateCapabilityGroupModel(
        name=new_name, displayName=new_name,
        runnerType=runner_type, sharedRunner=shared_runner,
        setupCommand=setup_command,
        sourceCode=source_code, functions=functions
    )
    payload_dict = capability_group.dict(exclude_none=True)

    # Update capability group
    response = httpx.put(endpoint, json=payload_dict,
                         headers=_get_headers())
    try:
        response.raise_for_status()
        capability_group_data = response.json().get("data", {})
        return _transform_capability_group_data(capability_group_data)
    except httpx.HTTPStatusError:
        return response.json()


async def update_capability_group_async(name: str,
                                        new_name: Optional[str] = None,
                                        runner_type: Optional[str] = None,
                                        shared_runner: Optional[bool] = None,
                                        setup_commands: Optional[List[str]] = None,
                                        source_code: Optional[str] = None,
                                        functions: Optional[List[Dict]] = None) -> Dict:
    """
    Asynchronously updates an existing capability group.

    Parameters
    ----------
    name : str
        The current name of the capability group.
    new_name : Optional[str], optional
        The new name of capability group to update to, by default None.
    runner_type : Optional[str], optional
        The type of runner, by default None.
    shared_runner : Optional[bool], optional
        Whether the runner is shared, by default None.
    setup_commands : Optional[List[str]], optional
        The setup commands, by default None.
    source_code : Optional[str], optional
        The source code, by default None.
    functions : Optional[List[Dict]], optional
        The functions, by default None.

    Returns
    -------
    Dict
        The result of the update operation.
    """
    capability_id = await _get_capability_id_by_name_async(name)

    endpoint = _get_base_endpoint_url() + f"/manifests/{capability_id}"

    if functions is not None:
        functions = [FunctionModel.validate({**func, "group": name}).dict() for func in functions]

    if setup_commands is None:
        setup_command = None
    else:
        setup_command = {"setupCommands": setup_commands}

    # fixes loss of source code on rename
    if new_name and source_code is None:
        # fetch source code in the case of name change to not lose reference
        source_path = os.path.join("/home/jovyan", ".functions", name, "source.py")

        if os.path.exists(source_path):
            with open(source_path, "r") as f:
                source_code = f.read()
        else:
            source_code = None

    # Validate payload and exclude None values
    capability_group = UpdateCapabilityGroupModel(
        name=new_name, displayName=new_name,
        runnerType=runner_type, sharedRunner=shared_runner,
        setupCommand=setup_command,
        sourceCode=source_code, functions=functions
    )
    payload_dict = capability_group.dict(exclude_none=True)

    async with httpx.AsyncClient() as client:
        response = await client.put(endpoint, json=payload_dict,
                                    headers=_get_headers())
        try:
            response.raise_for_status()
            capability_group_data = response.json().get("data", {})
            return _transform_capability_group_data(capability_group_data)
        except httpx.HTTPStatusError:
            return response.json()
