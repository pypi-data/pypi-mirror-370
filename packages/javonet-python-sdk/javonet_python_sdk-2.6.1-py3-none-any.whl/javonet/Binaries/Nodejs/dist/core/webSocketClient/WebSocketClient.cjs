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
var WebSocketClient_exports = {};
__export(WebSocketClient_exports, {
  WebSocketClient: () => WebSocketClient,
  clients: () => clients,
  messageQueue: () => messageQueue,
  processingQueues: () => processingQueues
});
module.exports = __toCommonJS(WebSocketClient_exports);
var import_Runtime = require("../../utils/Runtime.cjs");
const import_meta = {};
const requireDynamic = (0, import_Runtime.getRequire)(import_meta.url);
const WebSocketStateEnum = {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3
};
const WebSocketStateEvent = {
  OPEN: "open",
  CLOSE: "close",
  ERROR: "error",
  MESSAGE: "message"
};
let WebSocket = null;
const clients = {};
const messageQueue = {};
const processingQueues = {};
class WebSocketClient {
  /**
   * @param {string} url
   * @param {{ isDisconnectedAfterMessage: boolean }} options
   */
  constructor(url, options) {
    this.url = url;
    this.isDisconnectedAfterMessage = options?.isDisconnectedAfterMessage ?? false;
  }
  /** @type {wsClient | null} */
  get instance() {
    return clients[this.url] || null;
  }
  get isConnected() {
    return this.instance ? this.instance?.readyState === WebSocketStateEnum.OPEN : false;
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
          const response = await this._send(messageArray);
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
  _send(messageArray) {
    return new Promise((resolve, reject) => {
      const client = this.instance;
      if (client && this.isConnected) {
        client.send(
          /** @type {any} */
          messageArray
        );
        const messageHandler = (message) => {
          resolve(message);
          if (this.isDisconnectedAfterMessage) {
            this.disconnect();
          }
          client.removeListener(WebSocketStateEvent.MESSAGE, messageHandler);
        };
        client.on(WebSocketStateEvent.MESSAGE, messageHandler);
      } else {
        this._connect().then((client2) => {
          client2.send(
            /** @type {any} */
            messageArray
          );
          const messageHandler = (message) => {
            resolve(message);
            if (this.isDisconnectedAfterMessage) {
              this.disconnect();
            }
            client2.removeListener(WebSocketStateEvent.MESSAGE, messageHandler);
          };
          client2.on(WebSocketStateEvent.MESSAGE, messageHandler);
        }).catch(reject);
      }
    });
  }
  /**
   * Disconnects the WebSocket by terminating the connection and cleans up queues.
   */
  disconnect() {
    if (this.instance) {
      this.instance.close();
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
   * @returns {Promise<wsClient>} - A promise that resolves when the connection is established.
   */
  _connect() {
    if (!WebSocket && (0, import_Runtime.isNodejsRuntime)()) {
      try {
        WebSocket = requireDynamic("ws");
      } catch (error) {
        if (
          /** @type {{ code?: string }} */
          error.code === "MODULE_NOT_FOUND"
        ) {
          throw new Error("ws module not found. Please install it using npm install ws");
        }
        throw error;
      }
    }
    return new Promise((resolve, reject) => {
      if (!WebSocket) {
        return reject(new Error("ws client is null"));
      }
      let client = clients[this.url];
      if (!client) {
        client = new WebSocket(this.url);
        clients[this.url] = client;
      }
      client.on(WebSocketStateEvent.OPEN, () => resolve(client));
      client.on(WebSocketStateEvent.ERROR, (error) => reject(error));
      client.on(WebSocketStateEvent.CLOSE, () => {
        reject(new Error("Connection closed before receiving message"));
      });
    });
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  WebSocketClient,
  clients,
  messageQueue,
  processingQueues
});
