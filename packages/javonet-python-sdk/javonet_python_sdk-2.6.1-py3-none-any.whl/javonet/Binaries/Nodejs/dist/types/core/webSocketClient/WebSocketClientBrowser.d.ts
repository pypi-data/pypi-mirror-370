/**
 * @typedef {object} Options
 * @property {boolean} [isDisconnectedAfterMessage]
 */
/** @type {Record<string, WebSocket>} */
export const clients: Record<string, WebSocket>;
/** @type {Record<string, Array<{resolve: Function, reject: Function, messageArray: Int8Array}>>} */
export const messageQueue: Record<string, Array<{
    resolve: Function;
    reject: Function;
    messageArray: Int8Array;
}>>;
/** @type {Record<string, boolean>} */
export const processingQueues: Record<string, boolean>;
export type Options = {
    isDisconnectedAfterMessage?: boolean | undefined;
};
/**
 * WebSocketClient class that handles WebSocket connection, message sending, and automatic disconnection.
 */
export class WebSocketClientBrowser {
    /**
     * @param {string} url
     * @param {Options} [options]
     */
    constructor(url: string, options?: Options);
    /** @type {string} */
    url: string;
    /** @type {boolean} */
    isDisconnectedAfterMessage: boolean;
    /** @type {WebSocket | null} */
    get instance(): WebSocket | null;
    get isConnected(): boolean;
    /**
     * Sends messageArray through websocket connection with guaranteed order preservation
     * @async
     * @param {Int8Array} messageArray
     * @returns {Promise<Int8Array>}
     */
    send(messageArray: Int8Array): Promise<Int8Array>;
    /**
     * Processes message queue sequentially to maintain order
     * @private
     * @async
     */
    private _processMessage;
    /**
     * Sends a single message through websocket connection
     * @private
     * @async
     * @param {Int8Array} messageArray
     * @returns {Promise<Int8Array>}
     */
    private _sendSingle;
    /**
     * Disconnects the WebSocket by terminating the connection and cleans up queues.
     */
    disconnect(): void;
    /**
     * Connects to the WebSocket server.
     * @private
     * @async
     * @returns {Promise<WebSocket>}
     */
    private _connect;
    /**
     * Sends the data to the WebSocket server and listens for a response.
     * @private
     * @param {WebSocket} client
     * @param {Int8Array} data
     * @param {(value: Int8Array) => void} resolve
     * @param {(reason?: any) => void} reject
     */
    private _sendMessage;
}
