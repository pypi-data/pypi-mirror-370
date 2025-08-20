/**
 * WebSocketHandler class to manage WebSocket connections.
 */
export class WebSocketHandler {
    /**
     * Creates an instance of WebSocketHandler.
     * @param {string} url - The WebSocket server URL.
     * @param {function} onMessageCallback - The callback function to handle incoming messages.
     */
    constructor(url, onMessageCallback) {
        // Initialize WebSocket connection
        this.url = url;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.onMessageCallback = onMessageCallback;

        this.heartbeatInterval = 1000;
        this.heartbeatTimeout = 3000;
        this.pingTimeoutId = null;
        this.pongTimeoutId = null;

        this.connect();

    }

    /**
     * Connects to the WebSocket server.
     */
    connect() {
        this.ws = new WebSocket(this.url);

        // Add event listeners to the WebSocket instance
        this.ws.addEventListener('open', this.handleOpen);
        this.ws.addEventListener('message', this.handleMessage);
        this.ws.addEventListener('close', this.handleClose);
        this.ws.addEventListener('error', this.handleError);

    }

    // Event handlers
    handleOpen = () => {
        console.log('WebSocket connection opened');
        this.reconnectAttempts = 0;
        this.startHeartbeat();
    };

    handleMessage = (event) => {
        if (event.data === 'pong') {
            clearTimeout(this.pongTimeoutId);
            return;
        } else if (this.onMessageCallback) {
            this.onMessageCallback(event.data);
        }
    };

    handleClose = (event) => {
        console.warn('WebSocket connection closed:', event);
        clearInterval(this.pingTimeoutId);
        clearTimeout(this.pongTimeoutId);
        this.reconnect();
    };

    handleError = (event) => {
        console.error('WebSocket error:', event);
        clearInterval(this.pingTimeoutId);
        clearTimeout(this.pongTimeoutId);
        // in case of error, onclose will be called anyway, so no need to reconnect here
    };

    /**
     * Sends a message through the WebSocket connection.
     * @param {string | Blob} message - The message to be sent.
     */
    sendMessage(message) {
        // Check if the WebSocket connection is open before sending the message
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
        } else {
            console.error('WebSocket is not open. Cannot send message');
        }
    }

    /**
     * Reconnects to the WebSocket server.
     * Reconnects up to maxReconnectAttempts times with an exponential backoff delay.
     * If the maxReconnectAttempts is reached, the WebSocket connection is closed.
     */
    reconnect() {
        // close the WebSocket connection before reconnecting
        if (this.ws && this.ws.readyState !== WebSocket.CLOSED) {
            this.ws.close();
        }

        // clean up the WebSocket event listeners
        this.ws.removeEventListener('open', this.handleOpen);
        this.ws.removeEventListener('message', this.handleMessage);
        this.ws.removeEventListener('close', this.handleClose);
        this.ws.removeEventListener('error', this.handleError);

        // set reference to null to avoid memory leaks
        this.ws = null;

        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            console.log('Reconnecting...');
            setTimeout(() => {
                this.connect();
                this.reconnectAttempts++;
                this.reconnectDelay *= 2; // exponential backoff
            }, this.reconnectDelay);
        } else {
            console.error('Max reconnect attempts reached. Closing WebSocket connection');
            this.close();
        }

    }

    startHeartbeat() {
        clearInterval(this.pingTimeoutId);
        clearInterval(this.pongTimeoutId);

        this.pingTimeoutId = setInterval(() => {
            this.sendMessage('ping');
            this.pongTimeoutId = setTimeout(() => {
                console.error('ws-heartbeat timeout. Closing WebSocket connection');
                clearInterval(this.pingTimeoutId);
                clearTimeout(this.pongTimeoutId);
                this.ws.close();
            }, this.heartbeatTimeout);
        }, this.heartbeatInterval);
    }
        

    /**
     * Closes the WebSocket connection.
     */
    close() {
        // Check if the WebSocket instance exists before attempting to close it
        if (this.ws) {
            this.ws.close();
        }
    }
}
