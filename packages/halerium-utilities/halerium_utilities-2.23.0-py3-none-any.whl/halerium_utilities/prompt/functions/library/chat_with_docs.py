import asyncio
import difflib
import json
import os

from pathlib import Path

from halerium_utilities.prompt.models import call_model_async
from halerium_utilities.stores import get_information_store_by_name_async, create_information_store_async
from halerium_utilities.stores.api import get_information_store_info_async


INFO_STORE_NAME = "~chat_with_files"

SUPPORTED_FILES = (
    ".txt", ".md",
    ".html", ".py", ".ipynb",
    ".csv", ".xlsx", ".xlsm",
    ".pdf", ".docx", ".doc", ".pptx", ".ppt",
    ".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a", ".wma", ".aiff", ".opus",
    ".cpp", ".go", ".java", ".kt", ".js", ".ts", ".php", ".proto", ".py", ".rst",
    ".rb", ".rs", ".scala", ".swift", ".md", ".tex", ".sol", ".cs", ".cbl", ".c", ".lua", ".pl", ".hs",
)


async def _get_store():
    try:
        store = await get_information_store_by_name_async(INFO_STORE_NAME)
    except:
        store = await create_information_store_async(INFO_STORE_NAME)
    return store


async def _add_file(filepath, wait=True):
    store = await _get_store()

    mtime = round(os.path.getmtime(filepath))

    await store.add_file_async(filepath, metadata={"mtime": str(mtime)},
                               chunker_args={"embed_images": True, "use_ocr": "images"})

    workspace_filepath = _to_workspace_path(filepath)

    if not wait:
        return True

    for i in range(200):
        await asyncio.sleep(0.1)
        processes = (await get_information_store_info_async(store._store_id))["item"]["processes"]
        still_processing = False
        for p in processes:
            if workspace_filepath in p.get("description", ""):
                still_processing = True
                break
        if not still_processing:
            break

    description = await _generate_description(filepath)
    if description:
        await _update_description_chunk(workspace_filepath, description)

    return True


def _to_workspace_path(path):
    path = Path(path).resolve()
    prepared_path = str(path.relative_to("/home/jovyan"))
    if prepared_path == ".":
        prepared_path = ""
    if not prepared_path.startswith("/"):
        prepared_path = "/" + prepared_path
    return prepared_path


async def _get_all_path_chunks(filepath, startswith=False):
    store = await _get_store()
    workspace_filepath = _to_workspace_path(filepath)

    if startswith:
        workspace_filepath = workspace_filepath.rstrip("/")
        filters = [
            {"filter_type": "wildcard", "key": "source", "value": workspace_filepath + "/*"}
        ]
    else:
        filters = [
            {"filter_type": "exact_match", "key": "source", "value": workspace_filepath}
        ]

    all_chunks = []
    for i in range(100):
        chunks = await store.get_chunks_async(start=i * 1000, size=(i + 1) * 1000, filters=filters)
        if chunks:
            all_chunks += chunks
        else:
            break
    return all_chunks


async def _remove_file(filepath):
    all_chunks_to_delete = await _get_all_path_chunks(filepath, startswith=False)
    if all_chunks_to_delete:
        store = await _get_store()
        await store.delete_chunks_async([c["id"] for c in all_chunks_to_delete])


async def _is_file_recent(filepath):
    store = await _get_store()
    workspace_filepath = _to_workspace_path(filepath)
    mtime = round(os.path.getmtime(filepath))

    chunks = await store.query_library_async(query=None, max_results=1, filters=[
        {"filter_type": "exact_match", "key": "source", "value": workspace_filepath}
    ])

    if chunks:
        old_mtime = chunks[0]["metadata"].get("mtime", "0")
        if int(old_mtime) >= mtime:
            print("file is recent")
            return True
    else:
        print("file is changed")
        return False


async def _update_file(filepath, wait=True):
    if not filepath.lower().endswith(SUPPORTED_FILES):
        return True

    if not os.path.exists(filepath):
        await _remove_file(filepath)
        return True

    if await _is_file_recent(filepath):
        return True

    print("updating file")
    await _remove_file(filepath)
    await _add_file(filepath, wait=wait)

    return True


async def _get_all_chunked_files_in_dir(path):
    all_chunks = await _get_all_path_chunks(path, startswith=True)
    sources = {
        c.get("source") for c in all_chunks
    }
    files = ["/home/jovyan" + s for s in sources]
    return files


async def _update_directory(path, wait=True):
    chunked_files = await _get_all_chunked_files_in_dir(path)

    # Include the existing files in the directory tree
    existing_files = []
    for root, dirs, files in os.walk(path):
        # Remove hidden directories in-place
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.startswith('.'):
                continue
            existing_files.append(os.path.join(root, file))

    # Combine chunked files and existing files
    all_files = set(chunked_files + existing_files)

    semaphore = asyncio.Semaphore(10)

    async def sem_task(filepath):
        async with semaphore:
            await _update_file(filepath=filepath, wait=wait)

    tasks = [asyncio.create_task(sem_task(filepath)) for filepath in all_files]
    await asyncio.gather(*tasks)

    return


async def _update_path(path, wait=True):
    if not os.path.exists(path):
        # do both to ensure directory cleanup AND file cleanup
        await _update_directory(path, wait=wait)
        await _update_file(path, wait=wait)
    elif os.path.isdir(path):
        await _update_directory(path, wait=wait)
    else:
        await _update_file(path, wait=wait)


async def _generate_description(filepath):
    store = await _get_store()
    workspace_filepath = _to_workspace_path(filepath)

    filters = [
        {"filter_type": "exact_match", "key": "source", "value": workspace_filepath},
    ]

    chunks = await store.get_chunks_async(start=0, size=5, filters=filters, full_chunk_content=True)

    if len(chunks) == 0:
        return "file appears to be empty"

    content_preview = "\n".join([c["chunk"] for c in chunks])
    filename = os.path.basename(filepath)
    # num_pages = max([c["metadata"].get("page", 0) for c in chunks])

    prompt = f"Generate a 1 sentence description of the file {filename}."
    prompt += '\nAnswer in JSON format like this `{"description": (1-sentence description)}'
    prompt += '\nNote: if the content preview is empty it can mean that the file type is not supported.'
    prompt += f'\n\nContent preview:\n\n{content_preview}'

    body = {"messages": [{"role": "user", "content": prompt}], "temperature": 0,
            "response_format": {"type": "json_object"}}
    gen = call_model_async("chat-gpt-40-o-mini", body=body, parse_data=True)
    answer = ""
    async for event in gen:
        answer += event.data.get("chunk", "")

    try:
        description = json.loads(answer).get("description")
    except json.JSONDecodeError:
        description = None

    return description


async def _update_description_chunk(workspace_filepath, description):
    store = await _get_store()
    description_path = ".descriptions" + workspace_filepath
    filters = [
        {"filter_type": "exact_match", "key": "source", "value": description_path},
    ]
    chunks = await store.get_chunks_async(filters=filters, full_chunk_content=True)
    if chunks:
        await store.delete_chunks_async([c["id"] for c in chunks])

    await store.add_chunks_async([{
        "content": description,
        "metadata": {"source": description_path}
    }])


async def _get_description(filepath):
    store = await _get_store()
    workspace_filepath = _to_workspace_path(filepath)
    description_path = ".descriptions" + workspace_filepath
    filters = [
        {"filter_type": "exact_match", "key": "source", "value": description_path},
    ]
    chunks = await store.get_chunks_async(filters=filters, full_chunk_content=True)
    if chunks:
        return chunks[0]["chunk"]


async def list_dir(path="."):
    """
    List the contents of a directory.

    Parameters
    ----------
    path : str, optional
        Directory path to list contents of. Defaults to the current directory.

    Returns
    -------
    list of dict
        List of dictionaries containing file information (path, is_dir, description).
    """

    files = os.listdir(path)
    result = []
    for f in files:
        if f.startswith("."):
            continue
        full_path = os.path.join(path, f)
        d = {
            "path": f,
            "is_dir": os.path.isdir(full_path)
        }
        description = await _get_description(f)
        if description:
            d["description"] = description
        result.append(d)
    return result


async def search_file(path, extension=None, substring=None, typo_tolerance=True):
    """
    Search for files in the file system.

    Parameters
    ----------
    path : str
        Directory path to search within.
    extension : str, optional
        File extension to search for (e.g., ".pdf").
    substring : str, optional
        Substring to search for in file names.
    typo_tolerance : bool, optional
        Whether to include typo tolerance in the search.

    Returns
    -------
    list of str
        List of matching file paths.
    """
    if not (extension or substring):
        return "Please provide extension and/or substring"

    matching_files = []

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.startswith('.'):
                continue
            file_path = os.path.join(root, file)
            file_name_lower = file.lower()

            # Check for file extension match
            if extension and not file_name_lower.endswith(extension.lower()):
                continue

            # Check for substring match
            if substring:
                if substring.lower() in file_name_lower:
                    matching_files.append(file_path)
                elif typo_tolerance:
                    close_matches = difflib.get_close_matches(substring.lower(), [file_name_lower], n=1, cutoff=0.8)
                    if close_matches:
                        matching_files.append(file_path)
            else:
                if extension:
                    matching_files.append(file_path)

    return matching_files


async def semantic_search(path, query: str = None, example_text: str = None,
                          keywords: str = None, max_results: int = 5):
    """
    Perform a semantic search on the specified path.

    Parameters
    ----------
    path : str
        The file or directory path to search within.
    query : str, optional
        The search query.
    example_text : str, optional
        Example text to improve search relevance.
    keywords : str, optional
        Keywords to improve search relevance.
    max_results : int, optional
        Maximum number of search results to return.

    Returns
    -------
    list
        List of search results.
    """

    await _update_path(path, wait=True)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist.")

    workspace_filepath = _to_workspace_path(path)
    if os.path.isdir(path):
        workspace_filepath = workspace_filepath.rstrip("/")
        filters = [
            {"filter_type": "wildcard", "key": "source", "value": workspace_filepath + "/*"}
        ]
    else:
        filters = [
            {"filter_type": "exact_match", "key": "source", "value": workspace_filepath}
        ]

    store = await _get_store()
    results = await store.query_library_async(query=query, example_text=example_text, keywords=keywords,
                                              max_results=max_results, filters=filters)
    for r in results:
        metadata = r["metadata"]
        for key in ["mtime", "__created__", "image_b64"]:
            if key in metadata:
                del metadata[key]
        try:
            filepath = "/home/jovyan" + metadata["source"]
            relpath = os.path.relpath(filepath, ".")
            metadata["source"] = relpath
        except:
            pass
    return results


async def look_at_page(path, page: int):
    if not path.lower().endswith((".pdf", ".docx", ".doc", ".pptx", ".ppt")):
        return "Can only look at pages of .pdf, .docx, .doc, .pptx, .ppt files."

    await _update_path(path, wait=True)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist.")

    workspace_filepath = _to_workspace_path(path)
    filters = [
        {"filter_type": "exact_match", "key": "source", "value": workspace_filepath},
        {"field": "page", "gte": int(page), "lte": int(page)}
    ]

    store = await _get_store()
    results = await store.query_library_async(query=None, max_results=1, filters=filters)
    if results:
        image = results[0]["metadata"].get("image_b64")
        return {"result": {"data": [{
            "content": results[0]["content"],
            "image/png": image,
            "remark": "The image is not yet visible to the user. You can show it to the user by repeating the markdown tag in your answer, but only do this if showing the image is needed for you answer."}]}}
    else:
        return {"result": "No results found. Try a different page number."}
