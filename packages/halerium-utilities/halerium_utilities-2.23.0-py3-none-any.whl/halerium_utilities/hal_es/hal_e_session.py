import httpx
import os
import shutil

from copy import deepcopy
from pathlib import Path
from typing import Union
from urllib.parse import urljoin

from halerium_utilities.board import BoardNavigator
from halerium_utilities.collab import CollabBoard
from halerium_utilities.hal_es.hal_e import HalE
from halerium_utilities.logging.exceptions import PathLinkError, ElementTypeError
from halerium_utilities.prompt import apply_board_action, apply_board_action_async
from halerium_utilities.stores.api import get_file_as_text


class HalESession:
    """
    Class for Hal-E Sessions.
    """
    def __init__(self, hale: HalE):
        """
        Initializes a new HalESession instance.

        This constructor creates a session for a specific HalE board and initializes
        a CollabBoard instance representing the board.

        Parameters
        ----------
        hale : HalE
            The HalE instance that this session represents
        """
        self.hale = hale

        tenant = os.getenv("HALERIUM_TENANT_KEY", "")
        workspace = os.getenv("HALERIUM_PROJECT_ID", "")
        runner_id = os.getenv("HALERIUM_ID", "")
        base_url = os.getenv("HALERIUM_BASE_URL", "")
        url = urljoin(
            base_url,
            "/api"
            f"/tenants/{tenant}"
            f"/projects/{workspace}"
            f"/runners/{runner_id}"
            f"/token-access/hal-es/session/{self.hale.name}",
        )

        with httpx.Client() as client:
            response = client.post(
                url,
                json={},
                headers={"Content-Type": "application/json",
                         "halerium-runner-token": os.environ["HALERIUM_TOKEN"]}
            )
            response.raise_for_status()
            self.session_info = response.json()["data"]

        session_path = self.session_info["sessionContent"]["path"]
        full_session_path = Path.home() / session_path.lstrip("/")
        self.board = CollabBoard(path=full_session_path)

        self.session_url = urljoin(
            self.hale.init_url, self.session_info['halESessionId'])

        self._user_info = None

    @property
    def user_info(self):
        return self._user_info

    @user_info.setter
    def user_info(self, user_info: Union[dict, None]):
        if user_info is None:
            self._user_info = None
        else:
            username = str(user_info.get("username", ""))
            name = str(user_info.get("name", ""))
            name = name if name else None
            self._user_info = {
                "username": username,
                "name": name
            }

    def _aux_get_elements(self, resolve: bool):
        """
        Auxiliary function to retrieve the list of path elements from the board.

        Optionally resolves each element if it is linked to another node (e.g., card).

        Parameters
        ----------
        resolve : bool
            If True, attempts to resolve elements by following linked node IDs.
            If False, returns the raw elements as stored in the board.

        Returns
        -------
        list
            A list of path elements, either resolved or raw depending on the `resolve` flag.
        """
        if resolve:
            path_elements = [
                self.board.resolve_path_element(element) for element in self.board.path_elements]
        else:
            path_elements = self.board.path_elements
        
        return path_elements
    
    def get_elements(self, resolve=True):
        """
        Fetch the Hal-E path (elements)

        Parameters
        ----------
        resolve: bool, optional
            Whether to resolve the element wrt a linked card.
            The default is True.
        
        Returns
        -------
        list
            A list of Hal-E path elements
        """
        self.board.pull()
        return self._aux_get_elements(resolve)
    
    async def get_elements_async(self, resolve=True):
        """
        Fetch the Hal-E path (elements) asynchronously

        Parameters
        ----------
        resolve: bool, optional
            Whether to resolve the element wrt a linked card.
            The default is True.
        
        Returns
        -------
        list
            A list of Hal-E path elements
        """
        await self.board.pull_async()
        return self._aux_get_elements(resolve)

    def _aux_get_element_by_id(self, element_id: str, resolve: bool):
        """
        Auxiliary function to retrieve a specific path element by its ID.

        Optionally resolves the element if it is linked to another node.

        Parameters
        ----------
        element_id : str
            The ID of the path element to retrieve.
        resolve : bool
            If True, attempts to resolve the element by following its linked node ID.
            If False, returns the raw path element.

        Returns
        -------
        PathElement
            The requested path element, either resolved or raw depending on the `resolve` flag.
        """
        path_element = self.board.get_path_element_by_id(element_id)

        if resolve:
            return self.board.resolve_path_element(path_element)
        else:
            return path_element
        
    def get_element_by_id(self, element_id: str, resolve=True):
        """
        Fetch a specified Hal-E path element by id

        Parameters
        ----------
        element_id : str
            The ID of the path element to retrieve.
        resolve: bool, optional
            Whether to resolve the element wrt a linked card.
            The default is True.

        Returns
        -------
        PathElement
            A specific Hal-E path element
        """
        self.board.pull()
        return self._aux_get_element_by_id(element_id, resolve)

    async def get_element_by_id_async(self, element_id: str, resolve=True):
        """
        Fetch a specified Hal-E path element by id asynchronously

        Parameters
        ----------
        element_id : str
            The ID of the path element to retrieve.
        resolve: bool, optional
            Whether to resolve the element wrt a linked card.
            The default is True.

        Returns
        -------
        PathElement
            A specific Hal-E path element
        """
        await self.board.pull_async()
        return self._aux_get_element_by_id(element_id, resolve)

    def _aux_insert_text(self, path_element: str, text: str, field: str):
        """
        Auxiliary function to insert text into a specified field of a path element.

        This method updates the content of a given field in either a 'note' or 'bot' element.
        If the element is linked to a card, the update is applied to the card; otherwise,
        it is applied directly to the path element.

        Parameters
        ----------
        path_element : PathElement
            The path element to update (must be of type 'note' or 'bot').
        text : str
            The text to insert.
        field : str
            The specific field to update. Must be:
            - 'title' or 'message' for 'note' elements.
            - 'prompt_input' or 'prompt_output' for 'bot' elements.

        Raises
        ------
        ElementTypeError
            If the element type is invalid or the specified field is not allowed for that type.
        """
        element_type = path_element.type

        if element_type not in {"note", "bot"}:
            raise ElementTypeError(f"Cannot insert text into a '{path_element.type}' element. Must be 'note' or 'bot'.")

        if element_type == "note" and field not in {"title", "message"}:
            raise ElementTypeError(f"Field in a 'note' element must be of type 'title' or 'message'.")

        if element_type == "bot" and field not in {"prompt_input", "prompt_output"}:
            raise ElementTypeError(f"Field in a 'bot' element must be of type 'prompt_input' or 'prompt_output'.")

        card_id = path_element.type_specific.linkedNodeId
        if card_id:
            card_update = {
                "id": card_id,
                "type_specific": {field: text}
            }
            self.board.update_card(card_update)
        else:
            element_update = {
                "id": path_element.id,
                "type_specific": {field: text}
            }
            self.board.update_path_element(element_update)

    def insert_text(self, element_id: str, text: str, field: str):
        """
        Inserts text into any path element.

        Parameters
        ----------
        element_id : str
            The ID of the path element to update.
        text : str
            The text to insert into the path element.
        field : str
            Specifies the field within the path element where the value should be inserted. Must be one of: 'title', 'message', 'prompt_input', or 'prompt_output'.
        Returns
        -------
        Dict
            The updated path element.
        """
        path_element = self.get_element_by_id(element_id, resolve=False)
        self._aux_insert_text(path_element, text, field)
        self.board.push()

    async def insert_text_async(self, element_id: str, text: str, field: str):
        """
        Inserts text into any path element asynchronously.

        Parameters
        ----------
        element_id : str
            The ID of the path element to update.
        text : str
            The text to insert into the path element.
        field : str
            Specifies the field within the path element where the value should be inserted. Must be one of: 'title', 'message', 'prompt_input', or 'prompt_output'.
        Returns
        -------
        Dict
            The updated path element.
        """
        path_element = await self.get_element_by_id_async(element_id, resolve=False)
        self._aux_insert_text(path_element, text, field)
        await self.board.push_async()

    def send_prompt_with_input(self, element_id: str, prompt_input: str):
        """
        Sends user input and triggers the prompt on a 'bot' path element.

        Parameters
        ----------
        element_id : str
            The ID of the bot path element.
        prompt_input : str
            The user's input.

        Returns
        -------
        str
            The bot's answer.
        """
        self.insert_text(element_id=element_id, text=prompt_input, field="prompt_input")
        return self.send_prompt(element_id)
    
    async def send_prompt_with_input_async(self, element_id: str, prompt_input: str):
        """
        Sends user input and triggers the prompt on a 'bot' path element asynchronously.

        Parameters
        ----------
        element_id : str
            The ID of the bot path element.
        prompt_input : str
            The user's input.

        Returns
        -------
        str
            The bot's answer.
        """
        await self.insert_text_async(element_id=element_id, text=prompt_input, field="prompt_input")
        return await self.send_prompt_async(element_id)

    def send_prompt(self, element_id):
        """
        Triggers the prompt on a 'bot' path element.

        Parameters
        ----------
        element_id : str
            The ID of the bot path element.

        Returns
        -------
        str
            The bot's answer.
        """
        path_element = self.get_element_by_id(element_id, resolve=False)

        if path_element.type != "bot":
            raise ElementTypeError(f"Cannot send prompt to '{path_element.type}' element. Must be 'bot'.")

        card_id = path_element.type_specific.linkedNodeId
        if not card_id:
            raise PathLinkError("Bot element must be linked to a card to be evaluated.")

        self._execute_action(card_id)
        self.board.push()
        return self.board.get_card_by_id(card_id).type_specific.prompt_output
    
    async def send_prompt_async(self, element_id):
        """
        Triggers the prompt on a 'bot' path element asynchronously.

        Parameters
        ----------
        element_id : str
            The ID of the bot path element.

        Returns
        -------
        str
            The bot's answer.
        """
        path_element = await self.get_element_by_id_async(element_id, resolve=False)

        if path_element.type != "bot":
            raise ElementTypeError(f"Cannot send prompt to '{path_element.type}' element. Must be 'bot'.")

        card_id = path_element.type_specific.linkedNodeId
        if not card_id:
            raise PathLinkError("Bot element must be linked to a card to be evaluated.")

        await self._execute_action_async(card_id)
        await self.board.push_async()
        return self.board.get_card_by_id(card_id).type_specific.prompt_output

    def _aux_append_bot_element(self, path_element):
        """
        Auxiliary function to append a new bot element after an existing one in the path.

        This method creates a new bot card and path element, places it to the right
        of the existing bot card, connects the output of the original bot to the input
        of the new bot, and inserts the new path element immediately after the original.

        Parameters
        ----------
        path_element : PathElement
            The existing path element of type 'bot' to which a new bot element will be appended.

        Returns
        -------
        PathElement
            The newly created bot path element.

        Raises
        ------
        ElementTypeError
            If the provided path element is not of type 'bot'.
        PathLinkError
            If the path element is not linked to a card (i.e., missing linkedNodeId).
        """
        if path_element.type != "bot":
            raise ElementTypeError(f"Bot element can only be appended to element of type 'bot'. "
                                   f"Got element of type '{path_element.type}' instead.")
        card_id = path_element.type_specific.linkedNodeId
        if not card_id:
            raise PathLinkError("Bot element must be linked to a card to append to it.")

        path_element_index = self.board.path_elements.index(path_element)

        card = self.board.get_card_by_id(card_id)

        new_position = card.position.dict()
        new_position["x"] += card.size.width + 80

        new_card = self.board.create_card(
            type="bot",
            position=new_position
        )
        self.board.add_card(new_card)

        new_connection = self.board.create_connection(
            type="prompt_line",
            connections={
                "source": {
                    "connector": "prompt-output",
                    "id": card_id
                },
                "target": {
                    "connector": "prompt-input",
                    "id": new_card.id
                }
            }
        )
        self.board.add_connection(new_connection)

        new_element = self.board.create_path_element(
            type="bot",
            type_specific={
                "linkedNodeId": new_card.id
            }
        )
        self.board.add_path_element(new_element, index=path_element_index+1)
        return new_element
    
    def append_bot_element(self, element_id):
        """
        Appends a bot element to an existing bot element to continue a chat.

        Parameters
        ----------
        element_id : str
            The element_id of the bot element to append to.

        Returns
        -------
        new_element_id : str
            The id of the newly created bot element.
        """
        path_element = self.board.get_path_element_by_id(element_id)
        new_element = self._aux_append_bot_element(path_element)
        self.board.push()
        return new_element.id
    
    async def append_bot_element_async(self, element_id):
        """
        Appends a bot element to an existing bot element to continue a chat asynchronously.

        Parameters
        ----------
        element_id : str
            The element_id of the bot element to append to.

        Returns
        -------
        new_element_id : str
            The id of the newly created bot element.
        """
        path_element = self.board.get_path_element_by_id(element_id)
        new_element = self._aux_append_bot_element(path_element)
        await self.board.push_async()
        return new_element.id

    def _execute_action(self, card_id: str):
        """
        Executes a single action on a given card.

        Parameters
        ----------
        card_id : str
            The ID of the card to apply the action to.
        """
        self.board = apply_board_action(
            board=self.board,
            card_id=card_id,
            action="run",
            board_path=self.board.file_path.resolve().relative_to("/home/jovyan").as_posix(),
            user_info=self.user_info
        )

    async def _execute_action_async(self, card_id: str):
        """
        Executes a single action on a given card asynchronously.

        Parameters
        ----------
        card_id : str
            The ID of the card to apply the action to.
        """
        self.board = await apply_board_action_async(
            board=self.board,
            card_id=card_id,
            action="run",
            board_path=self.board.file_path.resolve().relative_to("/home/jovyan").as_posix(),
            user_info=self.user_info
        )

    def execute_actions(self, element_id: str):
        """
        Executes the action button specified by the element_id

        Parameters
        ----------
        element_id : str
            The ID of the action button element.
        """
        self.board.pull()
        navigator = BoardNavigator(board=self.board)
        bot_card_ids = navigator.get_action_element_executions(id=element_id)

        for card_id in bot_card_ids:
            self._execute_action(card_id)
            self.board.push()

        self.board.push()

    async def execute_actions_async(self, element_id: str):
        """
        Executes the action button specified by the element_id asynchronously

        Parameters
        ----------
        element_id : str
            The ID of the action button element.
        """
        await self.board.pull_async()
        navigator = BoardNavigator(board=self.board)
        bot_card_ids = navigator.get_action_element_executions(id=element_id)

        for card_id in bot_card_ids:
            await self._execute_action_async(card_id)
            await self.board.push_async()

        await self.board.push_async()

    def _get_unique_filename(self, directory, filename):
        base, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        while os.path.exists(os.path.join(directory, new_filename)):
            new_filename = f"{base}-{counter}{ext}"
            counter += 1
        return new_filename

    def _aux_upload_file(self, path_element, file_path: str):
        """
        Auxiliary function for handling file uploads to a Hal-E board path element.

        This method handles copying a local file into the appropriate Hal-E board
        directory, updating file path references and contents in linked cards.

        Parameters
        ----------
        path_element : PathElement
            The path element object representing the upload button.
        file_path : str
            The full path to the file to upload.

        Raises
        ------
        ElementTypeError
            If the provided path element is not of type 'upload'.

        Notes
        -----
        - Files are renamed if a file with the same name already exists in the target folder.
        - Both file path and file content targets of the path element are updated accordingly.
        """
        if path_element.type != "upload":
            raise ElementTypeError(f"Cannot upload a file to '{path_element.type}' element. Must be 'upload'.")

        board_path = self.session_info["sessionContent"]["path"]
        folder_name = Path(board_path).parent.name
        
        target_folder = os.path.dirname(board_path)
        target_folder_with_home = Path.home() / target_folder.lstrip('/')

        filename = os.path.basename(file_path)
        unique_filename = self._get_unique_filename(target_folder_with_home, filename)

        relative_path = f"{unique_filename}"

        target_path = os.path.join(target_folder_with_home, unique_filename)
        target_path_without_home = os.path.join(target_folder, unique_filename)

        shutil.copy(file_path, target_path)

        if path_element.type_specific.filePathTargets:
            for target in path_element.type_specific.filePathTargets:
                card_update = {
                    "id": target.targetId,
                    "type_specific": {"message": relative_path}
                }

                existing_message = self.board.get_card_by_id(target.targetId).type_specific.message
                updated_message = existing_message + "\n" + relative_path if existing_message else relative_path
                card_update["type_specific"]["message"] = updated_message

                self.board.update_card(card_update)

        if path_element.type_specific.fileContentTargets:
            for target in path_element.type_specific.fileContentTargets:
                chunker_args = path_element.type_specific.chunkingArguments
                file_content = get_file_as_text(target_path_without_home, chunker_args)
                card_update = {
                    "id": target.targetId,
                    "type_specific": {"message": file_content['item']}
                }

                existing_message = self.board.get_card_by_id(target.targetId).type_specific.message
                updated_message = (existing_message + "\n" + file_content['item']
                                   if existing_message else file_content['item'])
                card_update["type_specific"]["message"] = updated_message

                self.board.update_card(card_update)

        return target_path

    def upload_file(self, element_id: str, file_path: str):
        """
        Utilizes an upload button.
        The upload is emulated by copying the specified file to the target
        location of the upload button.

        Parameters
        ----------
        element_id : str
            The ID of the upload element.
        file_path : str
            The path of the file that is to be uploaded.
        """
        path_element = self.get_element_by_id(element_id, resolve=False)
        target_path = self._aux_upload_file(path_element, file_path)
        self.board.push()
        return target_path

    async def upload_file_async(self, element_id: str, file_path: str):
        """
        Utilizes an upload button asynchronously.
        The upload is emulated by copying the specified file to the target
        location of the upload button.

        Parameters
        ----------
        element_id : str
            The ID of the upload element.
        file_path : str
            The path of the file that is to be uploaded.
        """
        path_element = await self.get_element_by_id_async(element_id, resolve=False)
        target_path = self._aux_upload_file(path_element, file_path)
        await self.board.push_async()
        return target_path

    def __repr__(self):
        hale_name = self.hale.name
        session_path = self.session_info["sessionContent"]["path"]
        created_at = self.session_info["sessionContent"].get("created_at")

        return (f"HalESession(hale=HalE(name='{hale_name}'), session_url={self.session_url}, "
                f"session_path={session_path}, created_at='{created_at}')")

    @classmethod
    def from_hale_name(cls, hale_name: str) -> "HalESession":
        """
        Instantiates a HalESession based on a Hal-E name.

        Parameters
        ----------
        hale_name : str
            The name of the Hal-E on which to base the session..

        Returns
        -------
        HalESession
        """
        hal_e = HalE.from_name(hale_name)

        return cls(hale=hal_e)
