from pathlib import Path
from typing import List, Union, Optional, Dict

from halerium_utilities.logging.exceptions import InformationStoreException
from . import api


def get_information_store_by_name(name, case_sensitive=False):
    """
    Retrieve an information store by name.

    Parameters
    ----------
    name : str
        The name of the information store to retrieve.
    case_sensitive : bool, optional
        Whether the name search should be case-sensitive. Default is False.

    Returns
    -------
    InformationStore
        An already updated InformationStore instance.

    Raises
    ------
    InformationStoreException
        If the information store with the specified name is not found.
    """
    stores = api.get_workspace_information_stores()
    for store in stores['items']:
        store_name = store['name']
        if (case_sensitive and store_name == name) or (not case_sensitive and store_name.lower() == name.lower()):
            store_info = api.get_information_store_info(store['uuid'])
            return InformationStore(store['uuid'], store_info['item'])
    raise InformationStoreException(f"Information store with name '{name}' not found.")


async def get_information_store_by_name_async(name, case_sensitive=False):
    """
    Asynchronously retrieve an information store by name.

    Parameters
    ----------
    name : str
        The name of the information store to retrieve.
    case_sensitive : bool, optional
        Whether the name search should be case-sensitive. Default is False.

    Returns
    -------
    InformationStore
        An already updated InformationStore instance.

    Raises
    ------
    InformationStoreException
        If the information store with the specified name is not found.
    """
    stores = await api.get_workspace_information_stores_async()
    for store in stores['items']:
        store_name = store['name']
        if (case_sensitive and store_name == name) or (not case_sensitive and store_name.lower() == name.lower()):
            store_info = await api.get_information_store_info_async(store['uuid'])
            return InformationStore(store['uuid'], store_info['item'])
    raise InformationStoreException(f"Information store with name '{name}' not found.")


class InformationStore:

    def __init__(self, store_id, store_info=None):
        """
        Initialize the InformationStore instance.

        Parameters
        ----------
        store_id : str
            The unique identifier for the information store.
        store_info : dict, optional
            Information about the store, including name, memories, and vectorstore_id.
        """
        self._store_id = store_id
        self.name = None
        self.memories = None
        self.metadata_info = None
        self._vectorstore_id = None
        if store_info:
            self.name = store_info.get('name')
            self.memories = store_info.get('memories')
            vectorstores = store_info.get('vectorstores')
            if vectorstores and len(vectorstores) > 0:
                self._vectorstore_id = vectorstores[0]['id']

    def _check_vectorstore_id(self):
        if not self._vectorstore_id:
            raise InformationStoreException("Vectorstore ID is not set. Please run the `update` method first.")

    def update(self):
        """
        Update the information store with the latest data from the server.

        Returns
        -------
        dict
            Updated store information.
        """
        info = api.get_information_store_info(self._store_id)
        self.name = info['item']['name']
        self.memories = info['item']['memories']
        self.metadata_info = info['item']['metadata_info']
        vectorstores = info['item']['vectorstores']
        if vectorstores and len(vectorstores) > 0:
            self._vectorstore_id = vectorstores[0]['id']
        return info['item']

    async def update_async(self):
        """
        Asynchronously update the information store with the latest data from the server.

        Returns
        -------
        dict
            Updated store information.
        """
        info = await api.get_information_store_info_async(self._store_id)
        self.name = info['item']['name']
        self.memories = info['item']['memories']
        vectorstores = info['item']['vectorstores']
        if vectorstores and len(vectorstores) > 0:
            self._vectorstore_id = vectorstores[0]['id']
        return info['item']

    def rename(self, new_name):
        """
        Rename the information store.

        Parameters
        ----------
        new_name : str
            The new name for the information store.

        Returns
        -------
        dict
            Result of the rename operation.
        """
        api.rename_information_store(self._store_id, new_name)
        self.name = new_name

    async def rename_async(self, new_name):
        """
        Asynchronously rename the information store.

        Parameters
        ----------
        new_name : str
            The new name for the information store.

        Returns
        -------
        dict
            Result of the rename operation.
        """
        await api.rename_information_store_async(self._store_id, new_name)
        self.name = new_name

    def add_memory(self, memory: str):
        """
        Add a memory to the information store.

        Parameters
        ----------
        memory : str
            The memory to add to the store.

        Returns
        -------
        dict
            Result of the add memory operation.
        """
        return api.add_memory_to_store(self._store_id, memory)["item"]

    async def add_memory_async(self, memory: str):
        """
        Asynchronously add a memory to the information store.

        Parameters
        ----------
        memory : str
            The memory to add to the store.

        Returns
        -------
        dict
            Result of the add memory operation.
        """
        result = await api.add_memory_to_store_async(self._store_id, memory)
        return result["item"]

    def edit_memory(self, memory_id: str, memory: str):
        """
        Edit a memory in the information store.

        Parameters
        ----------
        memory_id : str
            The memory id to be edited in the store.
        memory : str
            The updated memory.
        """
        api.update_memory_in_store(self._store_id, memory_id, memory)

    async def edit_memory_async(self, memory_id: str, memory: str):
        """
        Asynchronously edit a memory in the information store.

        Parameters
        ----------
        memory_id : str
            The memory id to be edited in the store.
        memory : str
            The updated memory.
        """
        await api.update_memory_in_store_async(self._store_id, memory_id, memory)

    def delete_memory(self, memory_id: str):
        """
        Delete a memory in the information store.

        Parameters
        ----------
        memory_id : str
            The memory id to be deleted in the store.
        """
        api.delete_memory_in_store(self._store_id, memory_id)

    async def delete_memory_async(self, memory_id: str):
        """
        Asynchronously delete a memory in the information store.

        Parameters
        ----------
        memory_id : str
            The memory id to be deleted in the store.
        """
        await api.delete_memory_in_store_async(self._store_id, memory_id)

    @staticmethod
    def _prepare_file_path(path):
        path = Path(path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Could not locate {path}.")
        prepared_path = str(path.relative_to("/home/jovyan"))
        if not prepared_path.startswith("/"):
            prepared_path = "/" + prepared_path
        return prepared_path

    def add_file(self, filepath: str, chunker_args: Optional[Dict[str, Union[str, bool, List[str]]]] = None,
                 metadata: Optional[Dict[str, str]] = None, chunk_size: int = None, chunk_overlap: int = None):
        """
        Add a file to the vector store.

        Parameters
        ----------
        filepath : str
            The path to the file to add.
        chunker_args : dict, optional
            Arguments for the chunker.
        metadata : dict, optional
            Metadata for the file.
        chunk_size : int, optional
            The size of the chunks.
        chunk_overlap : int, optional
            The overlap between chunks.

        Returns
        -------
        dict
            Result of the add file operation.
        """
        self._check_vectorstore_id()
        filepath = self._prepare_file_path(filepath)
        api.add_file_to_vectorstore(self._vectorstore_id, filepath, chunker_args, metadata,
                                    chunk_size, chunk_overlap)

    async def add_file_async(self, filepath: str, chunker_args: Optional[Dict[str, Union[str, bool, List[str]]]] = None,
                             metadata: Optional[Dict[str, str]] = None, chunk_size: int = None,
                             chunk_overlap: int = None):
        """
        Asynchronously add a file to the vector store.

        Parameters
        ----------
        filepath : str
            The path to the file to add.
        chunker_args : dict, optional
            Arguments for the chunker.
        metadata : dict, optional
            Metadata for the file.
        chunk_size : int, optional
            The size of the chunks.
        chunk_overlap : int, optional
            The overlap between chunks.

        Returns
        -------
        dict
            Result of the add file operation.
        """
        self._check_vectorstore_id()
        filepath = self._prepare_file_path(filepath)
        await api.add_file_to_vectorstore_async(self._vectorstore_id, filepath, chunker_args,
                                                metadata, chunk_size, chunk_overlap)

    def add_chunks(self, chunks: List[Union[api.Document, dict]]):
        """
        Add chunks to the vector store.

        Parameters
        ----------
        chunks : list of Document or dict
            The chunks to add to the vector store.

        Returns
        -------
        dict
            Result of the add chunks operation.
        """
        self._check_vectorstore_id()
        return api.add_chunks_to_vectorstore(self._vectorstore_id, chunks)["items"]

    async def add_chunks_async(self, chunks: List[Union[api.Document, dict]]):
        """
        Asynchronously add chunks to the vector store.

        Parameters
        ----------
        chunks : list of Document or dict
            The chunks to add to the vector store.

        Returns
        -------
        dict
            Result of the add chunks operation.
        """
        self._check_vectorstore_id()
        result = await api.add_chunks_to_vectorstore_async(self._vectorstore_id, chunks)
        return result["items"]

    def query_library(self, query: str, example_text: str = None, keywords: str = None,
                      max_results: int = 5, threshold: int = -1,
                      filters: List[Union[api.RangeParam, api.SearchParam]] = None):
        """
        Query the vector store.

        Parameters
        ----------
        query : str
            The query string.
        example_text : str, optional
            Example text for the query.
        keywords : str, optional
            Keywords for the query.
        max_results : int, optional
            Maximum number of results to return.
        threshold : int, optional
            Threshold for the query.
        filters : list of RangeParam or SearchParam, optional
            Filters for the query.

        Returns
        -------
        dict
            Result of the query.
        """
        self._check_vectorstore_id()
        result = api.query_vectorstore(self._vectorstore_id, query, example_text, keywords,
                                       max_results, threshold, filters)
        return [
            {"content": content, "metadata": metadata}
            for content, metadata in zip(result["results"], result["metadata"])
        ]

    async def query_library_async(self, query: str, example_text: str = None, keywords: str = None,
                                  max_results: int = 5, threshold: int = -1,
                                  filters: List[Union[api.RangeParam, api.SearchParam]] = None):
        """
        Asynchronously query the vector store.

        Parameters
        ----------
        query : str
            The query string.
        example_text : str, optional
            Example text for the query.
        keywords : str, optional
            Keywords for the query.
        max_results : int, optional
            Maximum number of results to return.
        threshold : int, optional
            Threshold for the query.
        filters : list of RangeParam or SearchParam, optional
            Filters for the query.

        Returns
        -------
        dict
            Result of the query.
        """
        self._check_vectorstore_id()
        result = await api.query_vectorstore_async(self._vectorstore_id, query, example_text,
                                                   keywords, max_results, threshold, filters)
        return [
            {"content": content, "metadata": metadata}
            for content, metadata in zip(result["results"], result["metadata"])
        ]

    def get_chunks(self, start=0, size=1000, full_chunk_content=False,
                   filters: List[Union[api.RangeParam, api.SearchParam]] = None):
        """
        Retrieve chunks from the vector store.

        Parameters
        ----------
        start : int, optional
            The starting index for the chunks.
        size : int, optional
            The number of chunks to retrieve.
        full_chunk_content : bool, optional
            Whether to retrieve the full content of the chunks.
        filters : list of RangeParam or SearchParam, optional
            Filters for the chunks.

        Returns
        -------
        dict
            Result of the get chunks operation.
        """
        self._check_vectorstore_id()
        return api.get_chunks(self._vectorstore_id, start, size,
                              full_chunk_content, filters)["items"]

    async def get_chunks_async(self, start=0, size=1000, full_chunk_content=False,
                               filters: List[Union[api.RangeParam, api.SearchParam]] = None):
        """
        Asynchronously retrieve chunks from the vector store.

        Parameters
        ----------
        start : int, optional
            The starting index for the chunks.
        size : int, optional
            The number of chunks to retrieve.
        full_chunk_content : bool, optional
            Whether to retrieve the full content of the chunks.
        filters : list of RangeParam or SearchParam, optional
            Filters for the chunks.

        Returns
        -------
        dict
            Result of the get chunks operation.
        """
        self._check_vectorstore_id()
        result = await api.get_chunks_async(self._vectorstore_id, start, size,
                                            full_chunk_content, filters)
        return result["items"]

    def get_chunk(self, chunk_id: str):
        """
        Retrieve a specific chunk from the vector store.

        Parameters
        ----------
        chunk_id : str
            The ID of the chunk to retrieve.

        Returns
        -------
        dict
            Result of the get chunk operation.
        """
        self._check_vectorstore_id()
        return api.get_chunk(self._vectorstore_id, chunk_id)["item"]

    async def get_chunk_async(self, chunk_id: str):
        """
        Asynchronously retrieve a specific chunk from the vector store.

        Parameters
        ----------
        chunk_id : str
            The ID of the chunk to retrieve.

        Returns
        -------
        dict
            Result of the get chunk operation.
        """
        self._check_vectorstore_id()
        result = await api.get_chunk_async(self._vectorstore_id, chunk_id)
        return result["item"]

    def edit_chunk(self, chunk_id: str, document: Union[api.Document, dict]):
        """
        Edit a specific chunk in the vector store.

        Parameters
        ----------
        chunk_id : str
            The ID of the chunk to edit.
        document : Document or dict
            The new content for the chunk.

        Returns
        -------
        dict
            Result of the edit chunk operation.
        """
        self._check_vectorstore_id()
        api.edit_chunk(self._vectorstore_id, chunk_id, document)

    async def edit_chunk_async(self, chunk_id: str, document: Union[api.Document, dict]):
        """
        Asynchronously edit a specific chunk in the vector store.

        Parameters
        ----------
        chunk_id : str
            The ID of the chunk to edit.
        document : Document or dict
            The new content for the chunk.

        Returns
        -------
        dict
            Result of the edit chunk operation.
        """
        self._check_vectorstore_id()
        await api.edit_chunk_async(self._vectorstore_id, chunk_id, document)

    def delete_chunks(self, chunk_ids: List[str]):
        """
        Delete specific chunks from the vector store.

        Parameters
        ----------
        chunk_ids : list of str
            The IDs of the chunks to delete.

        Returns
        -------
        dict
            Result of the delete chunks operation.
        """
        self._check_vectorstore_id()
        api.delete_chunks(self._vectorstore_id, chunk_ids)

    async def delete_chunks_async(self, chunk_ids: List[str]):
        """
        Asynchronously delete specific chunks from the vector store.

        Parameters
        ----------
        chunk_ids : list of str
            The IDs of the chunks to delete.

        Returns
        -------
        dict
            Result of the delete chunks operation.
        """
        self._check_vectorstore_id()
        await api.delete_chunks_async(self._vectorstore_id, chunk_ids)


def create_information_store(name, case_sensitive=False):
    """
    Create a new information store if the name is not already occupied.

    Parameters
    ----------
    name : str
        The name of the new information store.
    case_sensitive : bool, optional
        Whether the name check should be case-sensitive. Default is False.

    Returns
    -------
    InformationStore
        An InformationStore instance of the newly created store.

    Raises
    ------
    InformationStoreException
        If an information store with the specified name already exists.
    """
    try:
        # Check if the store name is already occupied
        get_information_store_by_name(name, case_sensitive)
        raise InformationStoreException(f"Information store with name '{name}' already exists.")
    except InformationStoreException:
        # If not found, proceed to create the new store
        result = api.add_information_store(name)
        store_id = result['item']['id']
        store_info = api.get_information_store_info(store_id)
        return InformationStore(store_id, store_info['item'])


async def create_information_store_async(name, case_sensitive=False):
    """
    Asynchronously create a new information store if the name is not already occupied.

    Parameters
    ----------
    name : str
        The name of the new information store.
    case_sensitive : bool, optional
        Whether the name check should be case-sensitive. Default is False.

    Returns
    -------
    InformationStore
        An InformationStore instance of the newly created store.

    Raises
    ------
    InformationStoreException
        If an information store with the specified name already exists.
    """
    try:
        # Check if the store name is already occupied
        await get_information_store_by_name_async(name, case_sensitive)
        raise InformationStoreException(f"Information store with name '{name}' already exists.")
    except InformationStoreException:
        # If not found, proceed to create the new store
        result = await api.add_information_store_async(name)
        store_id = result['item']['id']
        store_info = await api.get_information_store_info_async(store_id)
        return InformationStore(store_id, store_info['item'])


def delete_information_store(info_store: Union[str, InformationStore]):
    """
    Delete an information store by its ID or instance.

    Parameters
    ----------
    info_store : str or InformationStore
        The ID or instance of the information store to delete.

    Returns
    -------
    dict
        Result of the delete operation.

    Raises
    ------
    InformationStoreException
        If the delete operation fails.
    """
    store_id = info_store if isinstance(info_store, str) else info_store._store_id
    api.delete_information_store(store_id)


async def delete_information_store_async(info_store: Union[str, InformationStore]):
    """
    Asynchronously delete an information store by its ID or instance.

    Parameters
    ----------
    info_store : str or InformationStore
        The ID or instance of the information store to delete.

    Returns
    -------
    dict
        Result of the delete operation.

    Raises
    ------
    InformationStoreException
        If the delete operation fails.
    """
    store_id = info_store if isinstance(info_store, str) else info_store._store_id
    await api.delete_information_store_async(store_id)

