"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);
var WebSocketClientBrowser_exports = {};
__export(WebSocketClientBrowser_exports, {
  WebSocketClientBrowser: () => WebSocketClientBrowser,
  clients: () => clients,
  messageQueue: () => messageQueue,
  processingQueues: () => processingQueues
});
module.exports = __toCommonJS(WebSocketClientBrowser_exports);
var import_Runtime = require("../../utils/Runtime.cjs");
const WebSocketState = (
  /** @type {const} */
  {
    OPEN: "open",
    CLOSE: "close",
    ERROR: "error",
    MESSAGE: "message"
  }
);
let WsClient = null;
if ((0, import_Runtime.isBrowserRuntime)()) {
  WsClient = WebSocket;
}
const clients = {};
const messageQueue = {};
const processingQueues = {};
class WebSocketClientBrowser {
  /**
   * @param {string} url
   * @param {Options} [options]
   */
  constructor(url, options) {
    this.url = url;
    this.isDisconnectedAfterMessage = options?.isDisconnectedAfterMessage ?? false;
  }
  /** @type {WebSocket | null} */
  get instance() {
    return clients[this.url] || null;
  }
  get isConnected() {
    return this.instance ? this.instance.readyState === WebSocket.OPEN : false;
  }
  /**
   * Sends messageArray through websocket connection with guaranteed order preservation
   * @async
   * @param {Int8Array} messageArray
   * @returns {Promise<Int8Array>}
   */
  send(messageArray) {
    return new Promise((resolve, reject) => {
      if (!messageQueue[this.url]) {
        messageQueue[this.url] = [];
      }
      messageQueue[this.url].push({ resolve, reject, messageArray });
      this._processMessage();
    });
  }
  /**
   * Processes message queue sequentially to maintain order
   * @private
   * @async
   */
  async _processMessage() {
    if (processingQueues[this.url]) {
      return;
    }
    processingQueues[this.url] = true;
    try {
      while (messageQueue[this.url] && messageQueue[this.url].length > 0) {
        const item = messageQueue[this.url].shift();
        if (!item) break;
        const { resolve, reject, messageArray } = item;
        try {
          const response = await this._sendSingle(messageArray);
          resolve(response);
        } catch (error) {
          reject(error);
        }
      }
    } finally {
      processingQueues[this.url] = false;
    }
  }
  /**
   * Sends a single message through websocket connection
   * @private
   * @async
   * @param {Int8Array} messageArray
   * @returns {Promise<Int8Array>}
   */
  _sendSingle(messageArray) {
    return new Promise((resolve, reject) => {
      const client = this.instance;
      if (client && this.isConnected) {
        this._sendMessage(client, messageArray, resolve, reject);
      } else {
        this._connect().then((ws) => {
          this._sendMessage(ws, messageArray, resolve, reject);
        }).catch(reject);
      }
    });
  }
  /**
   * Disconnects the WebSocket by terminating the connection and cleans up queues.
   */
  disconnect() {
    const client = this.instance;
    if (client) {
      client.close();
      delete clients[this.url];
    }
    if (messageQueue[this.url]) {
      messageQueue[this.url].forEach(({ reject }) => {
        reject(new Error("WebSocket disconnected"));
      });
      delete messageQueue[this.url];
    }
    delete processingQueues[this.url];
  }
  /**
   * Connects to the WebSocket server.
   * @private
   * @async
   * @returns {Promise<WebSocket>}
   */
  _connect() {
    return new Promise((resolve, reject) => {
      if (!WsClient) {
        return reject(new Error("missing WebSocket client"));
      }
      let client = clients[this.url];
      if (!client) {
        client = new WsClient(this.url);
        client.binaryType = "arraybuffer";
        clients[this.url] = client;
      }
      client.addEventListener(WebSocketState.OPEN, () => resolve(client));
      client.addEventListener(WebSocketState.ERROR, reject);
      client.addEventListener(WebSocketState.CLOSE, () => {
        reject(new Error("Connection closed before receiving message"));
      });
    });
  }
  /**
   * Sends the data to the WebSocket server and listens for a response.
   * @private
   * @param {WebSocket} client
   * @param {Int8Array} data
   * @param {(value: Int8Array) => void} resolve
   * @param {(reason?: any) => void} reject
   */
  _sendMessage(client, data, resolve, reject) {
    try {
      const arrayBuffer = data.buffer;
      client.send(arrayBuffer);
      const handleMessage = (message) => {
        if (!message?.data) {
          return reject(new Error("Invalid message received"));
        }
        const byteArray = new Int8Array(message?.data);
        resolve(byteArray);
        if (this.isDisconnectedAfterMessage) {
          this.disconnect();
        }
        client.removeEventListener(WebSocketState.MESSAGE, handleMessage);
        client.removeEventListener(WebSocketState.ERROR, handleError);
      };
      const handleError = (error) => {
        reject(error);
        client.removeEventListener(WebSocketState.MESSAGE, handleMessage);
        client.removeEventListener(WebSocketState.ERROR, handleError);
      };
      client.addEventListener(WebSocketState.MESSAGE, handleMessage);
      client.addEventListener(WebSocketState.ERROR, handleError);
    } catch (err) {
      reject(err);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  WebSocketClientBrowser,
  clients,
  messageQueue,
  processingQueues
});
