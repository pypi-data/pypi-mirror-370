import httpx
import os
from typing import List, Optional, Dict
from halerium_utilities.hal_es.schemas import HalEDataModel


def _get_endpoint():
    tenant = os.getenv('HALERIUM_TENANT_KEY', '')
    workspace = os.getenv('HALERIUM_PROJECT_ID', '')
    base_url = os.getenv('HALERIUM_BASE_URL', '')

    return f"{base_url}/api/tenants/{tenant}/projects/{workspace}/runners/{os.environ['HALERIUM_ID']}/token-access/hal-es"


def get_workspace_hales() -> List["HalE"]:
    """
    Fetches HalE instances for the workspace and converts the data into HalE objects.

    Returns
    -------
    List[HalE]
        A list of HalE instances representing available boards in the workspace.
    """
    raw_data = _get_workspace_hale_data()
    hales = []

    for hale_data in raw_data.get('data', []):
        hale_instance = _create_hale_from_data(hale_data)
        if hale_instance:
            hales.append(hale_instance)
        else:
            print(f"Failed to create HalE instance for: {hale_data}")

    return hales


async def get_workspace_hales_async() -> List["HalE"]:
    """
    Fetches available HalE instances in the workspace asynchronously.
    
    Returns
    -------
    List[HalE]
        A list of HalE instances representing available HalE boards in the workspace.
    """
    raw_data = await _get_workspace_hale_data_async()
    hales = []

    for hale_data in raw_data.get('data', []):
        hale_instance = _create_hale_from_data(hale_data)
        if hale_instance:
            hales.append(hale_instance)
        else:
            print(f"Failed to create HalE instance for: {hale_data}")

    return hales


def _get_workspace_hale_data() -> List[dict]:
    """
    Fetches raw data of available HalEs in the workspace.

    Returns
    -------
    List[dict]
        A list of dictionaries representing available HalE boards in the workspace.
    """
    endpoint = _get_endpoint()
    with httpx.Client() as client:
        response = client.get(
            endpoint,
            headers={"Content-Type": "application/json", "halerium-runner-token": os.environ["HALERIUM_TOKEN"]}
        )
        response.raise_for_status()
        return response.json()


async def _get_workspace_hale_data_async() -> List[dict]:
    """
    Fetches raw data of available HalEs in the workspace asynchronously.

    Returns
    -------
    List[dict]
        A list of dictionaries representing available HalE boards in the workspace.
    """
    endpoint = _get_endpoint()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            endpoint,
            headers={"Content-Type": "application/json", "halerium-runner-token": os.environ["HALERIUM_TOKEN"]}
        )
        response.raise_for_status()
        return response.json()


def _create_hale_from_data(hale_data: dict) -> Optional["HalE"]:
    """
    Creates a HalE instance from a hale_data.

    Parameters
    ----------
    hale_data : dict
        A dictionary containing the necessary keys to instantiate a HalE object.

    Returns
    -------
    Optional[HalE]
        A HalE instance if the provided data is valid, otherwise None.
    """

    access_rights = hale_data['appConfig']['accessType']
    template_board = hale_data['appConfig']['appParams']['sourcePath']
    name = hale_data['appConfig']['name']
    init_url = hale_data['friendlyUrl']

    hale_data_model = HalEDataModel(
        access_rights=access_rights, template_board=template_board,
        name=name, init_url=init_url
    )
    return HalE(hale_data_model)


class HalE:
    """
    Represents a HalE instance within a workspace.
    """

    def __init__(self, hale_data: HalEDataModel):
        """
        Initializes a HalE instance with the provided details.

        Parameters
        ----------
        hale_data : HalEDataModel
        """
        self.name = hale_data.name
        self.access_rights = hale_data.access_rights
        self.template_board = hale_data.template_board
        self.init_url = hale_data.init_url

    @classmethod
    def from_name(cls, hale_name: str) -> "HalE":
        hale_datas = _get_workspace_hale_data()
        for hale_data in hale_datas.get("data", []):
            if hale_data.get("appConfig", {}).get("name") == hale_name:
                return _create_hale_from_data(hale_data)
        raise ValueError(f"Could not find a Hal-E named '{hale_name}'.")

    def get_instance(self) -> Optional["HalESession"]:
        """
        Creates and returns a new HalESession instance for this HalE.

        Returns
        -------
        Optional[HalESession]
            Returns a HalESession instance if successful, or None if there is an issue.
        """
        from halerium_utilities.hal_es import HalESession

        return HalESession(self)

    def __repr__(self):
        return (f"HalE(name='{self.name}', access_rights='{self.access_rights}', "
                f"template_board='{self.template_board}', init_url='{self.init_url}')")
