"use strict";

/**
 * This JavaScript file defines a ChatManager class that handles a chat session between a user and an assistant.
 * The ChatManager is responsible for initializing the chat session, establishing a WebSocket connection,
 * handling incoming and outgoing messages, and managing the user interface.
 *
 * The ChatManager class includes methods to:
 * - Initialize the chat session and WebSocket connection
 * - Send messages from the user to the server
 * - Display messages from the user and the assistant in the chat interface
 * - Handle WebSocket messages and connectivity issues
 * - Append standalone and streamed messages to the chat interface
 * - Show and remove a "thinking" indicator for the assistant
 * - Scroll the chat to the latest message
 *
 * The code uses the 'marked' library to convert Markdown text to HTML and the 'hljs' library to highlight code blocks.
 *
 * The ChatManager is instantiated when the page loads, and it attaches event listeners to the chat and user input elements.
 */

/* imports */
import { getBaseUrl, getUrlParams } from "./url-handler.js";
import { AudioRecorder } from "./audio-recorder.js";
import { MarkdownRenderer } from "./markdown-renderer.js";
import { WebSocketHandler } from "./websocket-handler.js";

class ChatManager {
  /**
   * Constructor for ChatManager.
   * Initializes all necessary elements, sets up event listeners,
   * starts auto-scroll for chat, and initializes WebSocket connection.
   */
  constructor() {
    try {
      this.initializeSessionAndUrls();
      this.initializeChatElements();
      this.initializeInteractionElements();
      this.initializeGetInTouchAndByeMessage();
    } catch (error) {
      console.error("Error initializing chat elements:", error.message);
    }

    try {
      this.setupEventListeners();
    } catch (error) {
      console.error("Error setting up event listeners:", error.message);
    }

    try {
      this.wsHandler = new WebSocketHandler(
        this.appBaseUrl,
        this.sessionId,
        this.handleWsMessage.bind(this),
        this.handleWsConnectivityProblem.bind(this)
      );
      this.wsText = this.wsHandler.wsText;
      this.wsAudio = this.wsHandler.wsAudio;
    } catch (error) {
      console.error("Error initializing WebSocket connection:", error.message);
    }

    try {
      this.renderer = new MarkdownRenderer();
    } catch (error) {
      console.error("Error initializing Markdown renderer:", error.message);
    }

    try {
      this.queryParams = getUrlParams();

      // caller might include 'user' in the URL to set the user name
      // this overrides the user name set by the login
      if (this.queryParams["user"] && this.queryParams["user"] !== "null") {
        this.userName = this.queryParams["user"];
        this.updateUserName();
      }
    } catch (error) {
      console.error("Error getting URL parameters:", error.message);
    }

    try {
      this.audioContext = "";
      this.audioRecorder = new AudioRecorder([], (data) => {
        // handle messages from the audio worklet
        try {
          // send the binary audio data (16 bit PCM) to the server via websocket
          if (this.wsAudio.readyState === WebSocket.OPEN) {
            console.debug(
              `Sending audio data to backend: ${data.byteLength} bytes`
            );
            this.wsAudio.send(data);
          } else {
            console.error("WebSocket for audio is not open.");
          }
        } catch (error) {
          console.error(`Error sending audio stream to backend: ${error}`);
        }
      });
    } catch (error) {
      console.error("Error initializing audio recorder:", error.message);
    }

    this.autoScrollChat();
    this.evalInitialPrompt();
    this.userInput.focus();
  }

  /**
   * Initializes session details and URLs for WebSocket and application.
   */
  initializeSessionAndUrls() {
    try {
      this.sessionId = this.getSessionId("chatbot_session_id");
      this.appBaseUrl = getBaseUrl();
      this.initialPrompt = document.getElementById("initialPrompt").value;
      this.initialResponse = document.getElementById("initialResponse").value;
      this.byeMessage_personalized =
        document.getElementById("byeMessage").value;
    } catch (error) {
      console.error("Error initializing session and URLs:", error.message);
    }
  }

  /**
   * Initializes chat elements including bot name, user name, and message containers.
   */
  initializeChatElements() {
    this.botName = document.getElementById("botname").value;
    this.userName =
      document.getElementById("username").value !== ""
        ? document.getElementById("username").value
        : "User"; // can be overwritten by query parameters
    this.chat = document.getElementById("chat");
    this.messages = document.getElementById("messages");
  }

  /**
   * Initializes elements related to user interaction.
   */
  initializeInteractionElements() {
    this.userInputContainer = document.getElementById("user-input-container");
    this.userInput = document.getElementById("user-input");
    this.userInputOverlay = document.getElementById("user-input-overlay");
    this.shiftRPressed = false; // flag for shift + r key for recording voice
    this.sendOnEnterDisabled = false;
    this.startOverLink = document.getElementById("start-over-link");
    // append url params to start over link
    const urlParams = new URLSearchParams(document.location.search);

    if (urlParams) {
      this.startOverLink.href = `${this.appBaseUrl}${document.location.search}`;
    } else {
      this.startOverLink.href = `${this.appBaseUrl}`;
    }
  }

  /**
   * Initializes the contact link and the goodbye message for the chat.
   * TODO: this should be configurable by the user!
   */
  initializeGetInTouchAndByeMessage() {
    this.byeMessage = `Thank you for using ${this.botName}.`;
  }

  /**
   * Logs out the user by clearing cookies and redirecting to the login page.
   */
  logout(event) {
    event.preventDefault(); // Prevent the default link behavior
    const logoutUrl = `${this.appBaseUrl}logout`;

    fetch(logoutUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (response.ok) {
          // Redirect to the landing page
          window.location.href = this.appBaseUrl;
        } else {
          console.error("Logout failed:", response.statusText);
        }
      })
      .catch((error) => {
        console.error("Error during logout:", error.message);
      });
  }

  /**
   * Sets up various event listeners for chat and user input.
   */
  setupEventListeners() {
    this.setupChatScrollListener();
    this.setupInputListeners();
  }

  /**
   * Adds a scroll event listener to the chat element to handle auto-scrolling.
   */
  setupChatScrollListener() {
    this.chat.addEventListener("scroll", () => {
      this.autoScroll =
        this.chat.scrollTop + this.chat.clientHeight >=
        this.chat.scrollHeight - this.chat.scrollHeight / 100;
    });
  }

  /**
   * Sets up event listeners for user input, including send button and keyboard interactions.
   */
  setupInputListeners() {
    try {
      // Send Button Listener
      document
        .getElementById("send")
        ?.addEventListener("click", () =>
          this.sendMessage(this.getUserInput(), "prompt", false)
        );

      // Record Button Listener
      document
        .getElementById("record")
        ?.addEventListener("click", () => this.toggleRecordingVoice());

      // Global Keydown Listener
      document.addEventListener("keydown", (event) =>
        this.handleGlobalKeydown(event)
      );

      // download chat as board button listener
      document
        .getElementById("btn-download-as-board")
        ?.addEventListener("click", () => this.downloadChatAsBoard());

      // Logout link listener
      document
        .getElementById("logout-link")
        ?.addEventListener("click", (event) => this.logout(event));

      // User Input Listeners
      this.userInput?.addEventListener("input", () =>
        this.resetUserInputAreaSize()
      );
      this.userInput?.addEventListener("keydown", (event) =>
        this.handleUserInputKeydown(event)
      );
    } catch (error) {
      console.error("Error setting up input listeners:", error.message);
    }
  }

  /**
   * Copies the text content of a code block to the clipboard.
   * @param {HTMLElement} btn - The button element that was clicked.
   */
  copyToClipboard(btn) {
    var text = btn.nextElementSibling.textContent;
    navigator.clipboard
      .writeText(text)
      .then(function () {
        btn.textContent = "\u2713 Copied!"; // ✓
        setTimeout(() => {
          btn.textContent = "Copy code";
        }, 2000);
      })
      .catch(function (error) {
        console.error("Error in copying text: ", error.message);
      });
  }

  downloadChatAsBoard() {
    // fetch halerium board from backend
    const boardUrl = `${this.appBaseUrl}get_board/${this.sessionId}`;
    fetch(boardUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          console.error("Error fetching board:", response.statusText);
        }
      })
      .then((data) => {
        if (data) {
          console.log("Board data received:", data);

          const jsonString = JSON.stringify(data);

          console.log("Board data as JSON:", jsonString);

          // store data as a blob and assign an anchor to it
          const blob = new Blob([jsonString], { type: "application/json" });
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          const date = new Date();
          const year = date.getFullYear();
          const month = date.getMonth() + 1;
          const day = date.getDate();
          const hour = date.getHours();
          const minute = date.getMinutes();
          const second = date.getSeconds();
          const timestamp = `${year}-${month.toString().padStart(2, "0")}-${day
            .toString()
            .padStart(2, "0")}_${hour.toString().padStart(2, "0")}-${minute
            .toString()
            .padStart(2, "0")}-${second.toString().padStart(2, "0")}`;

          a.download = `${timestamp}_${this.sessionId}.board`;
          a.href = url;

          // add the anchor to the document and click it
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }
      })
      .catch((error) => {
        console.error("Error during board download:", error.message);
      });
  }

  /**
   * Handles keyboard key down events for the user input area.
   * @param {KeyboardEvent} event - The keyboard event.
   */
  handleUserInputKeydown(event) {
    // enter key: send message
    if (event.key === "Enter" && !event.shiftKey) {
      if (this.sendOnEnterDisabled === false) {
        event.preventDefault();
        this.sendMessage(this.getUserInput(), "prompt", false);
      } else {
        event.preventDefault();
        // do nothing.
      }
    }
    // shift + enter key: new line
    if (event.key === "Enter" && event.shiftKey) {
      event.preventDefault();
      this.userInput.value += "\n";
      this.resetUserInputAreaSize();
    }
  }

  /**
   * Handles keyboard key down events for the entire page.
   * @param {KeyboardEvent} event - The keyboard event.
   */
  handleGlobalKeydown(event) {
    // ctrl + shift + V: toggle recording voice
    if (event.ctrlKey && event.shiftKey && event.key === "V") {
      event.preventDefault();
      this.toggleRecordingVoice();
    }
  }

  /**
   * Handles incoming WebSocket messages.
   * @param {MessageEvent} event - The WebSocket message event.
   * @param {string} wsType - The type of WebSocket connection (text or audio).
   */
  handleWsMessage(event, wsType) {
    let parsedEvent = {};
    try {
      parsedEvent = JSON.parse(event.data);
    } catch (error) {
      parsedEvent = {
        event: "error",
        data: {
          chunk: "Error: The received message's format is incompatible.",
        },
      };
      console.error(`Error parsing WebSocket message: ${error.message}`);
    }

    switch (parsedEvent.event) {
      case "error":
        console.error(`Error from WebSocket: ${parsedEvent.data.chunk}`);
        this.removeThinkingIndicator();
        this.appendStandaloneMessageToChat(
          "assistant",
          "I'm sorry, but an error occurred while processing your message."
        );
        break;

      case "pong":
        // console.log("pong received");
        break;

      case "chunk":
        switch (wsType) {
          case "text":
            // check text for markdown images that contain "function:" in the filename
            const markdownImageRegex = /!\[.*?\]\((function:.*?)\)/g;
            const markdownImageMatches =
              parsedEvent.data.chunk.match(markdownImageRegex);

            // if a function call is detected in the markdown image, we don't want to append the message to the chat
            // as this is done via the function and function_output SSEs
            if (markdownImageMatches) {
              console.log("markdownImageMatches:", markdownImageMatches);
              console.log("breaking out of chunk processing");
            } else {
              console.log("chunk received");
              this.removeThinkingIndicator();
              this.appendStreamedMessageToChat(
                "assistant",
                parsedEvent.data.chunk || ""
              );
            }
            break;

          case "audio":
            if (this.userInput.value.length > 0) {
              if (
                this.userInput.value[this.userInput.value.length - 1] === " " ||
                this.userInput.value[this.userInput.value.length - 1] === "\n"
              ) {
                this.userInput.value += parsedEvent.data.chunk;
              } else {
                this.userInput.value += ` ${parsedEvent.data.chunk}`;
              }
            } else {
              this.userInput.value += parsedEvent.data.chunk;
            }

            // alternatively, we can send the chunk as a message to the server direclty:
            // this.sendMessage(parsedEvent.data.chunk, "prompt", false);

            // hide the overlay
            this.userInputOverlay.style.display = "none";
            this.userInput.disabled = false;
            this.disableUserInput(false);
            this.userInput.focus();
            this.resetUserInputAreaSize();
            break;
        }
        break;

      case "function":
        console.log("function received");
        this.removeThinkingIndicator();

        // Check if pretty_name exists and is not null or empty
        const functionName = parsedEvent.data.pretty_name || parsedEvent.data.function_name;

        this.appendStreamedMessageToChat(
          "assistant",
          `<span class="functionCallLabel" id="${parsedEvent.data.id}">⚡️ executing ${functionName}...</span>`
        );
        break;

      case "function_output":
        console.log("function_output received");
        this.removeThinkingIndicator();
        let currentFunctionCallLabel = document.getElementById(
          parsedEvent.data.id
        );
        currentFunctionCallLabel.textContent =
          currentFunctionCallLabel?.textContent
            .replace("⚡️ executing", "✅ executed")
            .replace("...", "");
        break;

      case "attachment":
        // console.log("attachment received");
        const currentTextSpan = document.getElementById("currSpan");
        const attachmentsDiv =
          currentTextSpan.parentElement.querySelector(".attachments");
        attachmentsDiv[parsedEvent.data["filename"]] =
          parsedEvent.data["attachment"];
        break;

      case "audio":
        var url = URL.createObjectURL(atob(parsedEvent.data.audio));
        var audio = new Audio(url);
        audio.play();
        break;
    }
  }

  /**
   * Handles connectivity issues with the WebSockets.
   * @param {CloseEvent} event - The WebSocket close event.
   */
  handleWsConnectivityProblem(event) {
    console.error(`WebSocket error observed: ${event.code}, ${event.reason}`);
    this.removeThinkingIndicator();
    this.appendStandaloneMessageToChat("assistant", this.byeMessage);
    this.scrollToBottomOfElement(chat);
  }

  async updateUserName() {
    const url = `${this.appBaseUrl}update_username/${this.sessionId}`;
    const formData = new FormData();
    formData.append("username", this.userName);

    try {
      const response = await fetch(url, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        console.log("User name updated successfully.");
      } else {
        console.error("Failed to update user name.");
      }
    } catch (error) {
      console.error("Error updating user name:", error.message);
    }
  }

  /**
   * Evaluates the initial prompt as defined on the chatbot Board.
   * If a initial response was found, it displays that in the chat instead.
   */
  evalInitialPrompt() {
    if (this.initialResponse === "" && this.initialPrompt !== "") {
      this.sendMessage(this.initialPrompt, "prompt", true);
    } else if (this.initialResponse !== "") {
      this.appendStandaloneMessageToChat("assistant", this.initialResponse);
    }
  }

  /**
   * Sends the user's message to the chat and performs necessary UI updates.
   * @param {string} - The message text to be sent.
   */
  sendMessage(query, promptType, isInitialPrompt) {
    let data = {
      type: promptType,
      sid: this.sessionId,
      isInitialPrompt: isInitialPrompt,
      queryParams: this.queryParams,
      query: "",
    };

    if (query === "") {
      console.debug("Empty query. Getting message from user input.");
      query = this.getUserInput();
    }

    if (query) {
      this.disableUserInput(true);
      // we only want to append the user query to the chat if it's not a prompt predefined in the chatbot board
      if (!isInitialPrompt) {
        this.appendStandaloneMessageToChat("user", query);
      }
      // add query to message
      data.query = query;

      this.sendMessageToServer(data);
      this.clearUserInput();
      this.showThinkingIndicator();
      this.scrollToBottomOfElement();
    }
  }

  /**
   * Sends the user's message to the server via WebSocket.
   * @param {dict} query - The message text to be sent.
   */
  sendMessageToServer(query) {
    try {
      if (this.wsText.readyState === WebSocket.OPEN) {
        const json_query = JSON.stringify(query);
        this.wsText.send(json_query);
      } else {
        if (this.wsText.readyState === WebSocket.CONNECTING) {
          console.warn("WebSocket is still connecting.");
          // just wait a second and try again
          setTimeout(() => {
            this.sendMessageToServer(query);
          }, 150);
        } else if (this.wsText.readyState === WebSocket.CLOSED) {
          console.error("Websocket is closed.");
          this.appendStandaloneMessageToChat(
            "assistant",
            "I'm sorry, but your message could not be sent."
          );
        }
      }
    } catch (error) {
      console.error(`Error sending message: ${error}`);
      this.appendStandaloneMessageToChat(
        "assistant",
        "I'm sorry, but your message could not be sent."
      );
      this.disableUserInput(false);
    }
  }

  /**
   * Toggles the recording of the user's voice.
   */
  toggleRecordingVoice() {
    // console.log(`isRecording: ${this.audioRecorder.isRecording}`)
    if (this.audioRecorder.isRecording) {
      document.getElementById("record").classList.remove("active-recording");
      // console.log(`set isRecording to ${this.audioRecorder.isRecording}.`)
      this.stopStreamingVoice();
    } else {
      document.getElementById("record").classList.add("active-recording");
      this.startStreamingVoice();
    }
  }

  /**
   * Records the user's voice.
   */
  async startStreamingVoice() {
    // send start signal to backend
    try {
      if (this.wsAudio.readyState === WebSocket.OPEN) {
        this.audioRecorder.isRecording = true;

        const r = await this.audioRecorder.setupAudioStreaming();

        if (r) {
          this.wsAudio.send(
            JSON.stringify({
              type: "audio-start",
              samplerate: this.audioRecorder.sampleRate,
            })
          );

          await this.audioRecorder.startRecording();

          // set this up last, so that the user knows that the recording is active
          console.debug("Audio streaming set up successfully:" + r);
          this.userInput.disabled = true;
          this.sendButtonDisabled(true);
          this.userInputOverlay.textContent = "Listening...";
          this.userInputOverlay.style.height = document.getElementById(
            "user-input-container"
          ).height;
          this.userInputOverlay.style.display = "block";
        } else {
          console.error("Error setting up audio streaming.");
        }
      }
    } catch (error) {
      console.error(`Error registering audio stream with backend: ${error}`);
    }
  }

  /**
   * Stops the recording of the user's voice.
   */
  stopStreamingVoice() {
    this.audioRecorder.stopRecording();

    if (this.wsAudio.readyState === WebSocket.OPEN) {
      // console.log("sending audio-end");
      this.userInputOverlay.textContent = "Processing recording...";
      this.recordButtonDisabled(true);
      this.wsAudio.send(JSON.stringify({ type: "audio-end" }));
    }
  }

  /**
   * disables all user input sending interactions
   * @param {bool} state
   */
  disableUserInput(state) {
    this.sendButtonDisabled(state);
    this.recordButtonDisabled(state);
    this.toggleSendOnEnterDisabled(state);
  }

  /**
   * Enables or disables the send button.
   * @param {boolean} state - True to disable the button, false to enable it.
   */
  sendButtonDisabled(state) {
    document.getElementById("send").disabled = state;
  }

  /**
   * Enables or disables the record button.
   * @param {boolean} state - True to disable the button, false to enable it.
   */
  recordButtonDisabled(state) {
    document.getElementById("record").disabled = state;
  }

  toggleSendOnEnterDisabled(state) {
    this.sendOnEnterDisabled = state;
  }

  /**
   * Automatically scrolls the chat content.
   * Continuously checks and adjusts the scroll position to reveal new messages.
   */
  autoScrollChat() {
    setInterval(() => {
      if (this.autoScroll) {
        this.chat.scrollTop = this.chat.scrollHeight;
      }
    }, 50);
  }

  /**
   * Returns the current value of the user input text area.
   */
  getUserInput() {
    return this.userInput.value.trim();
  }

  /**
   * Returns the current session ID from cookies.
   * @param {string} key - The name of the cookie.
   */
  getSessionId(key) {
    const id = document.cookie.match(new RegExp("(^| )" + key + "=([^;]+)"));
    if (id) {
      return id[2];
    } else {
      return "";
    }
  }

  /**
   * Returns the current timestamp as a string.
   * Format: dd.mm.yyyy, HH:MM:SS
   */
  static getCurrentTimestamp() {
    const date = new Date();
    const day = date.getDate().toString().padStart(2, "0");
    const month = (date.getMonth() + 1).toString().padStart(2, "0");
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, "0");
    const minutes = date.getMinutes().toString().padStart(2, "0");
    const seconds = date.getSeconds().toString().padStart(2, "0");
    return `${day}.${month}.${year}, ${hours}:${minutes}:${seconds}`;
  }

  /**
   * Clears the user input field and resets its size.
   */
  clearUserInput() {
    // clear prompt text field and resize it accordingly
    this.userInput.value = "";
    this.resetUserInputAreaSize();
  }

  /**
   * Dynamically adjusts the size of the user input area based on its content.
   * Ensures the chat interface accommodates the varying size of the input area.
   */
  resetUserInputAreaSize() {
    this.userInput.style.height = "auto";
    this.userInputContainer.style.height = "auto";
    this.userInput.style.height = this.userInput.scrollHeight + "px";
    this.userInputContainer.style.height = this.userInput.scrollHeight + "px";
  }

  createSenderItem(role) {
    const senderListItem = document.createElement("li");
    senderListItem.className = `sender-${role}`;

    const senderNameSpan = document.createElement("span");
    senderNameSpan.className = "name";
    senderNameSpan.textContent =
      role === "user" ? this.userName + " " : this.botName + " ";

    const timestampSpan = document.createElement("span");
    timestampSpan.className = "timestamp";
    timestampSpan.textContent = ChatManager.getCurrentTimestamp();

    senderListItem.appendChild(senderNameSpan);
    senderListItem.appendChild(timestampSpan);

    const messagesContainer = document.getElementById("messages");
    messagesContainer.appendChild(senderListItem);
  }

  createMessageItem(role, messageText) {
    const messageListItem = document.createElement("li");
    const messageTextSpan = document.createElement("span");

    messageListItem.className = `msg-${role}`;
    if (role === "assistant") {
      messageTextSpan.id = "currSpan";

      const imageDiv = document.createElement("div");
      imageDiv.classList.add("attachments");
      messageListItem.appendChild(imageDiv);
    }

    if (messageText) {
      messageTextSpan.textContent = messageText;

      if (role === "assistant") {
        this.parseMarkdown(messageTextSpan);
      }
    }
    messageListItem.appendChild(messageTextSpan);

    const messagesContainer = document.getElementById("messages");
    messagesContainer.appendChild(messageListItem);
  }

  /**
   * Appends a standalone message to the chat interface.
   * Used for messages that are not part of a streamed conversation.
   * @param {string} role - The role of the message sender (e.g., 'user', 'assistant').
   * @param {string} messageText - The text of the message to be appended.
   */
  appendStandaloneMessageToChat(role, messageText) {
    // create list item for sender and timestamp line
    this.createSenderItem(role);

    // create list item for message text
    this.createMessageItem(role, messageText);

    // remove the currSpan id if it was set because the role was assistant
    if (role === "assistant") {
      document.getElementById("currSpan").id = "";
    }
  }

  /**
   * Handles the appending of streamed messages to the chat interface.
   * This method manages the state of messages being received in parts.
   * @param {string} role - The role of the message sender (e.g., 'user', 'assistant').
   * @param {string} messageText - The text of the message or control tokens like <sos>, <eos>.
   */
  appendStreamedMessageToChat(role, messageText) {
    const currentTextSpan = document.getElementById("currSpan");
    switch (messageText) {
      case "<sos>":
        // create list item for sender and timestamp line
        this.createSenderItem(role);

        // create list item for message text
        this.createMessageItem(role, "");
        break;

      case "<eos>":
        // console.log(currentTextSpan.textContent);
        // parse markdown
        this.parseMarkdown(currentTextSpan);

        // highlight code blocks
        document
          .querySelectorAll("pre code:not(.highlighted)")
          .forEach((block) => {
            hljs.highlightElement(block);
            block.classList.add("highlighted");
          });
        currentTextSpan.id = "";
        this.disableUserInput(false);

        // scroll to bottom of chat
        this.scrollToBottomOfElement();
        break;

      case "<pong>":
        break;

      default:
        if (messageText) {
          currentTextSpan.innerHTML += messageText;
        }

        // scroll to bottom of chat
        this.scrollToBottomOfElement();
        // }
        break;
    }
  }

  getMimeType(filename) {
    const mimeTypes = {
      jpg: "image/jpeg",
      jpeg: "image/jpeg",
      png: "image/png",
      gif: "image/gif",
      bmp: "image/bmp",
      webp: "image/webp",
      tiff: "image/tiff",
      tif: "image/tiff",
      svg: "image/svg+xml",
      ico: "image/vnd.microsoft.icon",
      heic: "image/heic",
      heif: "image/heif",
    };

    const extension = filename.split(".").pop().toLowerCase();
    return mimeTypes[extension] || "application/octet-stream";
  }

  /**
   * Parses markdown text from an element and converts it into HTML.
   * Then sets the parsed content as innerHTML of that element.
   * @param {HTMLElement} el - The element containing the markdown text.
   */
  parseMarkdown(el) {
    // const value = el.textContent.trim();
    const value = el.getHTML().trim();
    const parsedValue = this.renderer.parseMarkdown(value);

    el.innerHTML = parsedValue;
    el.querySelectorAll(".halimg").forEach((img) => {
      const attachments = img
        .closest(".msg-assistant")
        .querySelector(".attachments");
      const filename = img
        .getAttribute("filename")
        .substr("attachments:".length - 1);
      const img_b64 = attachments[filename];
      const mime = this.getMimeType(filename);
      img.src = `data:${mime};base64,${img_b64}`;
    });
  }

  /**
   * Displays a visual indicator that the assistant is processing/thinking.
   * @param {string} [role='assistant'] - The role of the message sender.
   */
  showThinkingIndicator(role = "assistant") {
    const loadingListItem = document.createElement("li");
    loadingListItem.className = `msg-${role}`;
    loadingListItem.id = "loading-container";

    const loadingDots = document.createElement("div");
    loadingDots.className = "loading-dots";

    loadingListItem.appendChild(loadingDots);

    const messagesContainer = document.getElementById("messages");
    messagesContainer.appendChild(loadingListItem);
  }

  /**
   * Removes the thinking indicator from the chat interface.
   */
  removeThinkingIndicator() {
    const loadingContainer = document.getElementById("loading-container");
    if (loadingContainer) {
      loadingContainer.remove();
    }
  }

  /**
   * Scrolls the specified element to its bottom.
   * Typically used to keep the chat scrolled to the latest message.
   * @param {HTMLElement} [el=this.chat] - The element to scroll.
   */
  scrollToBottomOfElement(el = this.chat) {
    el.scrollTop = el.scrollHeight + 100;
  }
}

window.onload = () => {
  // document.getElementById("fmt").innerHTML = ChatManager.getCurrentTimestamp();
  window.chatManager = new ChatManager();
};
