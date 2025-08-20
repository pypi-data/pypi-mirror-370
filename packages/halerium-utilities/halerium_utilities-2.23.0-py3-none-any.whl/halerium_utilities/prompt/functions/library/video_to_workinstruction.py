import os
import base64
import json
import re
import shutil
import subprocess
import urllib
from pathlib import Path
from typing import Any, Dict, Union, Literal
from PIL import Image
from pydantic import BaseModel

from halerium_utilities.collab import CollabBoard
from halerium_utilities.prompt.models import call_model


base_url = os.getenv("HALERIUM_BASE_URL")
tenant_key = os.getenv("HALERIUM_TENANT_KEY")
project_id = os.getenv("HALERIUM_PROJECT_ID")

BASE_PREFIX = str(Path.home())


# --- Utility Functions ---
def get_current_dir():
    cwd = Path.cwd()
    return os.path.relpath(str(cwd), BASE_PREFIX)


def parse_input(input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Parses input that may be a JSON string or a dict."""
    if isinstance(input_data, str):
        try:
            return json.loads(input_data)
        except Exception:
            raise ValueError("Input string is not valid JSON.")
    elif isinstance(input_data, dict):
        return input_data
    else:
        raise ValueError("Input must be a dict or a JSON string.")


def get_config_value(config: dict, key: str, default: Any, typ: type) -> Any:
    """Extracts and casts config values to the desired type, including stringified lists."""
    value = config.get(key, default)
    try:
        if typ == list and isinstance(value, str):
            parsed_value = json.loads(value)
            if isinstance(parsed_value, list):
                return parsed_value
            else:
                return default
        if typ == bool:
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes")
            return bool(value)
        return typ(value)
    except Exception:
        return


def _get_filepath_in_outputs(filename: str) -> str:
    base, ext = os.path.splitext(filename)
    n = 1
    outputs_dir = "outputs"
    os.makedirs(outputs_dir, exist_ok=True)
    new_filename = os.path.join(outputs_dir, filename)
    while os.path.exists(new_filename):
        new_filename = os.path.join(outputs_dir, f"{base}-{n}{ext}")
        n += 1
    return os.path.relpath(os.path.abspath(new_filename))


def save_output_to_file(data: Any, filename: str, is_dict=True) -> str:
    """
    Saves data to a new unique file (with -{n} suffix if needed) and returns the file path.
    Does not rename existing files.
    """
    new_filename = _get_filepath_in_outputs(filename)
    with open(new_filename, "w", encoding="utf-8") as f:
        if is_dict:
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            # Write data directly as string
            f.write(str(data))

    return os.path.relpath(os.path.abspath(new_filename))


def load_output_from_file(filename: str) -> Any:
    """Loads data from a JSON file."""
    abs_file_name = os.path.abspath(filename)
    with open(abs_file_name, "r", encoding="utf-8") as f:
        return json.load(f)


# --- Main Pipeline Functions ---


def validate_video_file(video_path: str) -> bool:
    video_path_val = video_path if isinstance(video_path, str) else str(video_path)
    cwd = get_current_dir()
    video_path_val = (
        video_path_val
        if video_path_val.startswith(cwd)
        else os.path.join(cwd, video_path_val)
    )

    valid = False
    size = None
    try:
        size = _validate_video_path(video_path_val)
        valid = True
    except Exception as e:
        valid = False

    return video_path_val, valid, size


def preprocess_video(
        video_path: str, config_parameters: Union[str, dict] = None
) -> str:
    """
    Video Preprocessing.
    Extracts frames and audio from a video file, processes the frames for quality, and returns paths and metadata.
    Outputs a .json file with the results and returns its file path.
    """
    video_path_val, valid, size = validate_video_file(video_path)
    if not valid:
        raise FileNotFoundError(f"File does not exist: {video_path_val}")

    config = parse_input(config_parameters) if config_parameters else {}

    framerate = get_config_value(config, "framerate", 5, int)
    file_type = get_config_value(config, "file_type", "mp3", str)
    method = get_config_value(config, "method", "sobel", str)
    threshold = get_config_value(config, "threshold", 0.5, float)

    base_folder, image_folder, audio_url, full_image_paths = _vap_process(
        video_path_val, framerate=framerate, file_type=file_type
    )
    image_qa_image_urls = _image_qa_process(image_folder, method, threshold)
    output = {
        "base_folder": base_folder,
        "image_folder": image_folder,
        "audio_url": audio_url,
        "all_image_paths": full_image_paths,
        "image_qa_image_urls": image_qa_image_urls,
    }

    preprocess_output_path = save_output_to_file(output, "preprocess_video_output.json")
    transcription_output_path = _audio_transcription_process(
        audio_url, config_parameters
    )
    return preprocess_output_path, transcription_output_path


def view_raw_content(
        transcription_output_path: str,
        preprocess_output_path: str,
        config_parameters: Union[str, dict] = None,
) -> str:
    # Load transcription
    transcript = load_output_from_file(transcription_output_path)

    # Load preprocess output for image_folder
    if isinstance(preprocess_output_path, dict):
        preprocess_output = preprocess_output_path
    else:
        preprocess_output = load_output_from_file(preprocess_output_path)
    image_qa_image_urls = preprocess_output["image_qa_image_urls"]
    result = _group_images_by_sentences(
        transcript, [img_data["imageUrl"] for img_data in image_qa_image_urls]
    )
    content_path = save_output_to_file(result, "raw_content_data.json")
    html_view = _render_sentence_image_review(result)
    html_view_path = save_output_to_file(html_view, "raw_wi_content.html", False)
    md_view_path = save_output_to_file(html_view, "raw_wi_content.md", False)
    return html_view_path


def extract_timestamped_steps(
        transcription_output_path: str,
        preprocess_output_path: str,
        config_parameters: Union[str, dict] = None,
) -> str:
    """
    Draft Work Instructions.
    Aligns transcript sentences with video frames, generating a structured JSON.
    Inputs should be the file paths to the transcription_output.json and preprocess_output.json.
    Returns the file path to the output JSON file containing the draft instructions.
    """
    # Load transcription
    transcript = load_output_from_file(transcription_output_path)

    # Load preprocess output for image_folder
    if isinstance(preprocess_output_path, dict):
        preprocess_output = preprocess_output_path
    else:
        preprocess_output = load_output_from_file(preprocess_output_path)
    image_folder = preprocess_output["image_folder"]

    config = parse_input(config_parameters) if config_parameters else {}
    fps = get_config_value(config, "fps", 5, float)

    try:
        wi_result_data = build_timestamped_steps(transcript, image_folder, fps=fps)
        return save_output_to_file(wi_result_data, "timestamped_steps.json")
    except ValueError as exc:
        save_output_to_file(str(exc), "timestamped_steps_error.txt", is_dict=False)
        return "building timestamped steps failed"


def select_images_for_steps(
        timestamped_steps_path: str,
        preprocess_output_path: str,
        config_parameters: Union[str, dict] = None,
) -> str:
    """
    Finalize Work Instructions Markdown.
    Compiles step-by-step work instructions, timestamps, and selected images into a Markdown document.
    Inputs should be the file paths to the draft_instructions_output.json and preprocess_output.json.
    Returns the file path to the output JSON file containing the final instructions.
    Also saves a Markdown file.
    """
    # Load draft instructions
    wi_draft = load_output_from_file(timestamped_steps_path)
    steps_val = wi_draft["steps"]
    activity_title = wi_draft["activity"]

    # Load preprocess output for image_folder and image_qa_image_urls
    if isinstance(preprocess_output_path, dict):
        preprocess_output = preprocess_output_path
    else:
        preprocess_output = load_output_from_file(preprocess_output_path)
    image_folder = preprocess_output["image_folder"]
    image_qa_image_urls = preprocess_output["image_qa_image_urls"]

    config = parse_input(config_parameters) if config_parameters else {}
    top_n = get_config_value(config, "top_n", 1, int)
    fps = get_config_value(config, "fps", 5, float)

    image_urls = [Path(qa_output.get("imageUrl")) for qa_output in image_qa_image_urls]
    batches = _batch_data(steps=steps_val, image_urls=image_urls, top_n=top_n, fps=fps)
    save_output_to_file(batches, "batched_outputs.json")

    ica_result = _gen_helper(
        model_name="v2wi-image-captioning",
        body={"imageCaptioningRequests": batches, "imageFolder": image_folder},
    )
    final_images = json.loads(ica_result[0].get("data"))["topNimagesPerSentence"]
    # enrich wi with images
    for i, step in enumerate(steps_val):
        relative_image_paths = [
            os.path.relpath("/home/jovyan/" + p.lstrip("/"))
            for p in final_images[i]
        ]
        step["top_images"] = relative_image_paths
        if batches[i]["imageUrls"]:
            min_image_path = os.path.relpath("/home/jovyan/" + batches[i]["imageUrls"][0].lstrip("/"))
            max_image_path = os.path.relpath("/home/jovyan/" + batches[i]["imageUrls"][-1].lstrip("/"))
            step["image_range"] = {"first": min_image_path, "last": max_image_path}
        else:
            step["image_range"] = None

    return save_output_to_file(wi_draft, "timestamped_steps_w_images.json")


def read_work_instructions(workinstructions_path: str):
    """
    Reads and returns the contents of the specified work instructions Markdown file.

    Args:
        workinstructions_path (str): Path to the work_instructions.md file to be read.

    Returns:
        str: The contents of the file as a string, or an error message if the file is not found.
    """
    try:
        abs_workinstructions_path = os.path.abspath(workinstructions_path)
        with open(abs_workinstructions_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"{workinstructions_path} not found."


def read_and_display_output(output_path: str):
    return json.dumps(load_output_from_file(output_path), indent=2)


def create_deeplink(output_path: str, external: bool):
    file_path = os.path.join(get_current_dir(), output_path)
    safe_url = str(file_path).replace(" ", "%20")

    if external:
        return f"{base_url}/api/tenants/{tenant_key}/projects/{project_id}/contents/{safe_url}?download=inline"
    return f"{base_url}/{tenant_key}/{project_id}/contents/{safe_url}"


async def update_workinstruction(card_id: str, action: str, __halerium_card, config_parameters={}):
    path = __halerium_card["path"]
    collab_board = CollabBoard("/home/jovyan/" + path.lstrip("/"), pull_on_init=False)
    await collab_board.pull_async()
    raw_text = collab_board.get_card_by_id(card_id).type_specific.message

    separator = config_parameters.get("separator_line", "<separator index={{}}/>")

    # Extract separators and text blocks
    pattern = separator.replace('{{}}', r'(\d+)')
    matches = re.split(pattern, raw_text)

    text_blocks = matches[::2]  # Extract text blocks
    text_blocks = [t.strip("\n") for t in text_blocks]

    separator_indices = matches[1::2]  # Extract separator indices

    def find_insert_index(index):
        for i, s_index in enumerate(separator_indices):
            if int(s_index) > int(index):
                return i
            if int(s_index) == int(index):
                return i + 1
        return len(text_blocks)

    def find_update_index(index):
        if index == 0:
            return 0
        for i, s_index in enumerate(separator_indices):
            if int(s_index) == int(index):
                return i + 1

    action = json.loads(action)

    action_type = action.get("type")
    if action_type == "insert":
        index = int(action.get("index", 10 ** 6))
        contents = action.get("contents")
        if not isinstance(contents, list):
            return "'contents' must be a list for 'insert' action."
        index = find_insert_index(index)
        for i, c in enumerate(contents):
            text_blocks.insert(index + i, c)
        separator_indices.insert(index, str(index + 1))
    elif action_type == "delete":
        indices = [int(i) for i in action.get("indices", [])]
        indices = sorted(indices)
        checked_indices = []
        # first check that all indices exist
        for index in indices:
            ind = find_update_index(index)
            if ind is None:
                return f"Index {index} could not be found."
            checked_indices += [ind]
        # the deleted backwards order
        for index in checked_indices[::-1]:
            text_blocks.pop(index)
    elif action_type == "update":
        index = int(action.get("index"))
        index = find_update_index(index)
        if index is None:
            return f"Index {index} could not be found."
        content = action.get("content")
        text_blocks[index] = content
    else:
        return f"Action type {action_type} not known."

    updated_text = ""
    preview_text = ""
    counter = 0
    for text in text_blocks:
        t = text.strip("\n")
        if t:
            if counter > 0:
                updated_text += "\n\n" + separator.replace("{{}}", str(counter)) + "\n\n"
                preview_text += "\n\n" + separator.replace("{{}}", str(counter)) + "\n\n"
            updated_text += t
            preview_text += t[:20] + "[...]"
            counter += 1

    collab_board.update_card({"id": card_id, "type_specific": {"message": updated_text}})
    await collab_board.push_async()
    return {"status": "success", "preview": preview_text}


def create_gif_from_range(first_image_path, last_image_path, speed=2, config_parameters={}):
    config = parse_input(config_parameters) if config_parameters else {}
    extraction_fps = get_config_value(config, "fps", 5, float)
    gif_fps = extraction_fps * speed

    # Get directory and all files in it
    directory = os.path.dirname(first_image_path)
    all_files = os.listdir(directory)

    # Filter for image files (you can adjust extensions as needed)
    image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'))]
    image_files.sort()  # Alphabetical order

    # Get base names
    first_name = os.path.basename(first_image_path)
    last_name = os.path.basename(last_image_path)

    # Find indices
    try:
        start_idx = image_files.index(first_name)
        end_idx = image_files.index(last_name)
    except ValueError:
        raise ValueError("First or last image not found in directory.")

    # Get the range
    if start_idx > end_idx:
        raise ValueError("First image comes after last image alphabetically.")
    selected_images = image_files[start_idx:end_idx + 1]

    # Load images
    images = [Image.open(os.path.join(directory, img)) for img in selected_images]

    # Construct output name
    first_base = os.path.splitext(first_name)[0]
    last_base = os.path.splitext(last_name)[0]
    output_name = f"{first_base}_{last_base}.gif"
    output_path = _get_filepath_in_outputs(output_name)

    # Calculate duration per frame in milliseconds
    duration = int(1000 / gif_fps)

    # Save GIF
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0
    )
    return output_path


async def save_workinstruction(card_id: str, __halerium_card, config_parameters={}):
    path = __halerium_card["path"]
    collab_board = CollabBoard("/home/jovyan/" + path.lstrip("/"), pull_on_init=False)
    await collab_board.pull_async()
    raw_text = collab_board.get_card_by_id(card_id).type_specific.message

    separator = config_parameters.get("separator_line", "<separator index={{}}/>")

    # Extract separators and text blocks
    pattern = separator.replace('{{}}', r'(\d+)')
    matches = re.split(pattern, raw_text)

    text_blocks = matches[::2]  # Extract text blocks
    text_blocks = [t.strip("\n") for t in text_blocks]

    cleaned_text = ""
    for i, text in enumerate(text_blocks):
        if i > 0:
            cleaned_text += "\n\n"
        cleaned_text += text

    cleaned_text = _replace_sandbox_images(cleaned_text)

    # save the markdown text
    markdown_path = save_output_to_file(cleaned_text, "workinstruction.md", is_dict=False)

    docx_path = markdown_path[:-3] + ".docx"
    return {
        "markdown_path": markdown_path,
        "doxc_path": _markdown_to_docx(markdown_path, docx_path)
    }


async def push_wi_to_chatbot(wi_name, markdown_path, config_parameters={}):
    wi_path = config_parameters.get("wi_path", "/home/jovyan/work_instructions/")

    with open(markdown_path, "r") as f:
        markdown_text = f.read()

    # Regex to find all image tags and capture alt text and path
    image_tag_regex = r'!\[(.*?)\]\((.*?)\)'

    def replace_and_copy(match):
        alt_text, image_link = match.groups()
        image_filename = os.path.basename(image_link)
        source_path = image_link
        destination_dir = os.path.join(wi_path, wi_name)
        destination_path = os.path.join(destination_dir, image_filename)

        # Ensure destination directory exists
        os.makedirs(destination_dir, exist_ok=True)

        # Copy the image
        shutil.copy(source_path, destination_path)

        # New sandbox tag
        workspace_path = os.path.relpath(destination_path, "/home/jovyan")
        workspace_path = "/" + workspace_path.lstrip("/")
        quoted_dest = urllib.parse.quote(workspace_path, safe="/")
        new_tag = f'![{alt_text}](sandbox:{quoted_dest})'
        return new_tag

    # Replace all image tags and copy images
    markdown_text = re.sub(image_tag_regex, replace_and_copy, markdown_text)

    # Write the modified markdown text to the wiki
    output_md_path = os.path.join(wi_path, wi_name + ".md")
    with open(output_md_path, "w") as f:
        f.write(markdown_text)

    return "push complete"


REGEX_SANDBOX_IMAGE = r"""!\[[^\]]*\]\(sandbox:(?P<img_sandbox>[^\)]*)(?=\"|\))(\"[^\)]*\")?\)"""


def _replace_sandbox_images(cleaned_text):
    def replacer(match):
        # 1. Extract the path
        img_sandbox = match.group('img_sandbox')
        # 2. Unquote
        img_path = urllib.parse.unquote(img_sandbox)
        # 3. Make absolute
        abs_path = os.path.abspath(img_path)
        # 4. Build new tag (preserve alt text if you want)
        alt_text = match.group(0).split('](')[0][2:]  # crude alt extraction
        return f'![{alt_text}]({abs_path})'

    # 5. Replace all occurrences
    return re.sub(REGEX_SANDBOX_IMAGE, replacer, cleaned_text)


def _markdown_to_docx(markdown_path, docx_path):
    # Create a named temporary file
    subprocess.run(['pandoc', markdown_path, '-o', docx_path], check=True)
    return docx_path


# --- Supporting Functions ---


def _render_sentence_image_review(groups):
    """
    Takes a list of dicts with keys: 'sentences' (list of str), 'images' (list of str)
    Returns a string with markdown h3 for the sentence and a grid of images in HTML.
    """
    halerium_content_path = (
        f"{base_url}/api/tenants/{tenant_key}/projects/{project_id}/contents/"
    )
    output = []
    output_md = []
    for group in groups:
        # Use the first sentence (assuming one per group as in your example)
        sentence = group["sentences"][0]
        start = group.get("start", 0)
        end = group.get("end", 0)
        # Format timestamps to two decimal places
        start_str = f"{start:.2f}"
        end_str = f"{end:.2f}"
        output_md.append(f"[{start_str} - {end_str}]\n" f"### {sentence}" f"</div>\n")
        output.append(
            f'<div class="sentence">'
            f'<span class="timestamp">[{start_str} - {end_str}]</span> '
            f"<h3>{sentence}</h3>"
            f"</div>\n"
        )

        grid_start = (
            '<div class="image-grid" style="display: flex; flex-wrap: wrap; gap: 8px;">'
        )
        output_md.append(grid_start)
        output.append(grid_start)
        for img_path in group["images"]:
            dir_path = "/".join(img_path.split("/")[:-1])
            # Extract the frame file name
            frame_file = img_path.split("/")[-1]
            # Insert 'thumbs' before the filename
            new_src = f"{dir_path}/thumbs/{frame_file}?download=inline"
            img_output = f'<img src="{halerium_content_path}{new_src}" alt="{frame_file}" title="{frame_file}" style="width:auto; height:auto;">'
            output_md.append(img_output)
            output.append(img_output)
            output_md.append("</div>\n")
        output.append("</div>\n")
    return "\n".join(output)


def _audio_transcription_process(
        audio_url: str, config_parameters: Union[str, dict] = None
) -> str:
    """
    Audio Transcription.
    Transcribes the audio file specified in the preprocess_video output JSON.
    Input should be the file path to the preprocess_video_output.json.
    Returns the file path to the output JSON file containing the transcription results.
    If keywords exist in config_parameters and len(keywords) > 0, they are added to the model call.
    """
    audio_url = (
        audio_url
        if audio_url.startswith(str(Path.home()))
        else f"{str(Path.home())}/{audio_url}"
    )

    config = parse_input(config_parameters) if config_parameters else {}
    model = get_config_value(config, "model", "nova-3", str)
    keywords = get_config_value(config, "keywords", [], list)

    print("\nTranscribing audio:", audio_url)
    with open(audio_url, "rb") as f:
        b64_audio = base64.b64encode(f.read()).decode("utf-8")

    body = {"audio": b64_audio, "model": model}
    if keywords and len(keywords) > 0:
        body["keywords"] = keywords

    tra_result = _gen_helper(model_name="nova2", body=body)
    output = tra_result[0].get("data", {}).get("paragraphs", {}).get("paragraphs", [])
    return save_output_to_file(output, "audio_transcription_output.json")


def build_timestamped_steps(
        transcript_data: list, image_folder: str, fps: float = 5
):
    print("\nBuilding timestamped sentences")
    paragraphs = transcript_data

    timestamped_sentences = []
    if paragraphs:
        for para in paragraphs:
            timestamped_sentences.extend([
                DrafterTimestampedElement(
                    element=s.get("text"),
                    type="text",
                    start=s.get("start"),
                    end=s.get("end"),
                )
                for s in para.get("sentences", [])
            ])

    print("image folder", image_folder)
    b64_imgs = {}

    abs_image_folder = Path("/home/jovyan/" + image_folder)
    for im in abs_image_folder.glob("*.jpg"):
        with open(im, "rb") as f:
            b64_imgs[im.stem] = base64.b64encode(f.read()).decode("utf-8")

    timestamped_images = [
        DrafterTimestampedElement(
            element=enc, type="image_url", start=int(name.split("_")[-1]) / fps
        )
        for name, enc in b64_imgs.items()
    ]

    timestamped_images = sorted(timestamped_images, key=lambda x: x.start)
    print("Number of images:", len(timestamped_images))
    sampled_timestamped_images = timestamped_images[
                                 :: max(1, len(timestamped_images) // 50)
                                 ][:50]

    print(
        f"Finished creating user prompts with text and images. {len(timestamped_sentences)} sentences and {len(sampled_timestamped_images)} images will be sent."
    )

    wid_result = _gen_helper(
        model_name="v2wi-drafter",
        body={
            "userPrompts": [el.model_dump(mode="json") for el in timestamped_sentences]
                           + [im.model_dump(mode="json") for im in sampled_timestamped_images],
            "systemPrompt": None,
            "model": "chat-gpt-41",
            "temperature": 0.0,
            "jsonMode": True,
            "b64Mode": True,
        },
    )

    result = wid_result[0]["data"]
    # check result
    if "activity" not in result or "steps" not in result:
        raise ValueError(f"Building timestamped steps failed: {result}")

    return result


def _batch_data(steps: list, image_urls: list, top_n: int, fps: float = 5) -> list:
    batched_data = []
    timestamped_images = [
        {"ts": int(im.stem.split("_")[-1]) / fps, "url": im} for im in image_urls
    ]

    for idx, step in enumerate(steps):
        step_images = []

        if idx == len(steps) - 1:
            batched_data.append(
                {
                    "topN": top_n,
                    "sentence": step.get("stepDesc"),
                    "imageUrls": [str(im.get("url")) for im in timestamped_images],
                }
            )
        else:
            while (
                    timestamped_images
                    and timestamped_images[0]["ts"]
                    <= steps[idx + 1]["stepTimestamp"]["start"]
            ):
                im = timestamped_images.pop(0)
                step_images.append(im["url"])

            batched_data.append(
                {
                    "topN": top_n,
                    "sentence": step.get("stepDesc"),
                    "imageUrls": [str(url) for url in step_images],
                }
            )

    return batched_data


def _validate_video_path(video_path_input):
    print(f"Validating video_path: {video_path_input}")
    video_path = Path(video_path_input)
    size = None
    if not video_path.exists():
        local_video_path = Path.home() / video_path
        if not local_video_path.exists():
            raise FileNotFoundError(f'"{video_path}" does not exist.')
        size = local_video_path.stat().st_size
    elif not video_path.is_file():
        raise ValueError(f'"{video_path}" is not a valid file.')
    else:
        size = video_path.stat().st_size

    return size


def _vap_process(video_path: str, framerate=5, file_type="mp3"):
    _validate_video_path(video_path)
    print(f"Extracting frames and audio from video {video_path}")
    vap_result = _gen_helper(
        model_name="v2wi-videoaudio-processor",
        body={
            "videoUrl": str(video_path),
            "extractionFrameRate": framerate,
            "audioExportFiletype": file_type,
        },
    )

    result = json.loads(vap_result[1]["data"])
    base_folder = result.get("output_folder")
    image_folder = result.get("frame_extraction_folder")
    audio_url = base_folder + "/" + result.get("audio_extraction")
    full_image_paths = _get_frame_filepaths(image_folder)

    return base_folder, image_folder, audio_url, full_image_paths


def _group_images_by_sentences(transcript_data, image_paths, fps=5):
    # Helper to extract frame number from image path
    def get_frame_number(path):
        match = re.search(r"frame_(\d+)\.jpg", path)
        return int(match.group(1)) if match else None

    # Build a mapping from time to image path
    frame_to_time = {}
    for path in image_paths:
        frame_num = get_frame_number(path)
        if frame_num is not None:
            # frame_000001.jpg is at t=0s
            time = (frame_num - 1) / fps
            frame_to_time[path] = time

    # Flatten sentences from paragraphs
    sentences = []
    for para in transcript_data:
        for s in para["sentences"]:
            sentences.append({"start": s["start"], "end": s["end"], "text": s["text"]})

    # Group images for each sentence
    output = []
    for sent in sentences:
        start = sent["start"]
        end = sent["end"]
        # Select images whose timestamp falls within the sentence
        images_in_range = [
            path for path, t in frame_to_time.items() if start <= t < end
        ]
        output.append(
            {
                "start": start,
                "end": end,
                "sentences": [sent["text"]],
                "images": images_in_range,
            }
        )

    return output


def _image_qa_process(
        image_folder: str, method="sobel", threshold=0.5, hashFunc="dhash", maxDistance=5
):
    print(f"\nProcessing frames in {image_folder} for quality")
    iqa_result = _gen_helper(
        model_name="v2wi-image-qa",
        body={
            "imageFolder": image_folder,
            "method": method,
            "threshold": threshold,
            "hashFunc": hashFunc,
            "maxDistance": maxDistance,
        },
    )

    return json.loads(iqa_result[1]["data"])["images"]


def _format_work_instructions_markdown(steps: list, activity_title: str) -> str:
    markdown_output = f"### {activity_title}\n\n"

    for i, step in enumerate(steps):
        desc = step["step_description"]
        start = round(step["timestamp"]["start"], 2)
        end = round(step["timestamp"]["end"], 2)
        markdown_output += f"{i + 1}. {desc}\n"
        markdown_output += f"    - Video Timestamp: {start} - {end}\n"
        for img_url in step["images"]:
            safe_url = str(img_url).replace(" ", "%20")
            filename = Path(img_url).name
            markdown_output += f"    {_get_image_md(filename, safe_url, False)}\n"
        markdown_output += "\n"

    return markdown_output


def _get_image_md(filename, safe_image_path, sandbox=False):
    if sandbox:
        img_url = f"sandbox://{safe_image_path}"
    else:
        img_url = f"{base_url}/api/tenants/{tenant_key}/projects/{project_id}/contents/{safe_image_path}?download=inline"

    return f"![{filename}]({img_url})\n"


def _get_frame_filepaths(
        frame_extraction_folder: str, valid_exts={".jpg", ".jpeg", ".png"}
) -> list[str]:
    """
    Return a sorted list of paths relative to home directory for image files in the given folder.

    Args:
        frame_extraction_folder (str): Absolute or relative path to the image folder.
        valid_exts (set): Allowed image file extensions.

    Returns:
        list[str]: List of file paths relative to home directory.
    """
    home_path = str(Path.home())

    # Resolve frame_extraction_folder to absolute path if relative
    if not os.path.isabs(frame_extraction_folder):
        abs_path = os.path.join(home_path, frame_extraction_folder)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Folder does not exist: {frame_extraction_folder}")
        frame_extraction_folder = abs_path
    else:
        if not os.path.exists(frame_extraction_folder):
            raise FileNotFoundError(f"Folder does not exist: {frame_extraction_folder}")

    file_paths = sorted(
        os.path.join(frame_extraction_folder, f)
        for f in os.listdir(frame_extraction_folder)
        if os.path.isfile(os.path.join(frame_extraction_folder, f))
        and os.path.splitext(f)[1].lower() in valid_exts
    )

    # Convert to paths relative to home directory
    relative_paths = [os.path.relpath(path, home_path) for path in file_paths]

    return relative_paths


def _gen_helper(model_name: str, body: dict, ignore_conclusion: bool = True) -> list:
    response = call_model(model_name=model_name, body=body)

    responses = []
    for sse in response:
        event = sse.event
        data = json.loads(sse.data)

        if ignore_conclusion and event == "conclusion":
            continue

        responses.append({"event": event, "data": data})

    return responses


# --- Data Model ---


class DrafterTimestampedElement(BaseModel):
    element: str
    type: Literal["text", "image_url"]
    start: float = 0.0
    end: float = 0.0
