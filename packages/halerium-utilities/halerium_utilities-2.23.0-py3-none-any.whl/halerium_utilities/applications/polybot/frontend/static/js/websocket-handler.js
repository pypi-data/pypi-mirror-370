export class WebSocketHandler {
  constructor(baseUrl, sessionId, onMessageCallback, onCloseCallback) {
    try {
      this.baseUrl = baseUrl;
      // replace http or https with ws or wss
      this.baseUrl = this.baseUrl.replace(/^https?/, "ws");
      this.sessionId = sessionId;
      this.wsText = null;
      this.wsAudio = null;
      this.callback = onMessageCallback;
      this.onCloseCallback = onCloseCallback;

      this.init();
    } catch (error) {
      console.error("Error creating WebSocketHandler", error.message);
    }
  }

  init() {
    try {
      // websocket for text messages
      this.wsText = new WebSocket(
        `${this.baseUrl}/ws/text?token=${this.sessionId}`
      );
      this.wsText.binaryType = "blob";
      this.wsText.onmessage = (event) => this.callback(event, "text");
      this.wsText.onclose = (event) => this.onCloseCallback(event);
      this.wsText.onerror = (error) => {
        console.error(
          "WebSocket for text encountered an error:",
          error.message
        );
      };
    } catch (error) {
      console.error("Error creating WebSocket for text", error.message);
    }

    try {
      // websocket for audio messages
      this.wsAudio = new WebSocket(
        `${this.baseUrl}/ws/voice?token=${this.sessionId}`
      );
      this.wsAudio.onmessage = (event) => this.callback(event, "audio");
      this.wsAudio.onclose = (event) =>
        console.log(
          `WebSocket for voice closed: ${event.code}, ${event.reason}`
        );
      this.wsAudio.onerror = (error) => {
        console.error(
          "WebSocket for voice encountered an error:",
          error.message
        );
      };
    } catch (error) {
      console.error("Error creating WebSocket for voice", error.message);
    }

    // start the ping-pong mechanism
    this.wsPingPong();
  }

  /**
   * Sends a periodic 'ping' message over WebSocket to keep the connection alive.
   */
  wsPingPong() {
    try {
      setInterval(() => {
        if (this.wsText.readyState === WebSocket.OPEN) {
          try {
            this.wsText.send(
              JSON.stringify({ type: "ping", sid: this.sessionId })
            );
          } catch (error) {
            console.error(`Ping for wsText failed: ${error.message}`);
          }
        }
      }, 30000);
    } catch (error) {
      console.error(
        `Setting up ping mechanism for wsText failed: ${error.message}`
      );
    }

    try {
      setInterval(() => {
        if (this.wsAudio.readyState === WebSocket.OPEN) {
          try {
            this.wsAudio.send(
              JSON.stringify({ type: "ping", sid: this.sessionId })
            );
          } catch (error) {
            console.error(`Ping for wsAudio failed: ${error.message}`);
          }
        }
      }, 30000);
    } catch (error) {
      console.error(
        `Setting up ping mechanism for wsAudio failed: ${error.message}`
      );
    }
  }
}
