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
var TransmitterWebsocketBrowser_exports = {};
__export(TransmitterWebsocketBrowser_exports, {
  TransmitterWebsocketBrowser: () => TransmitterWebsocketBrowser
});
module.exports = __toCommonJS(TransmitterWebsocketBrowser_exports);
var import_WebSocketClientBrowser = require("../webSocketClient/WebSocketClientBrowser.cjs");
class TransmitterWebsocketBrowser {
  /**
   * @returns {void}
   */
  static initialize() {
  }
  /**
   * @returns {void}
   */
  static activate() {
  }
  /**
   * @async
   * @param {Int8Array} messageByteArray
   * @param {IConnectionData} connectionData
   * @returns {Promise<Int8Array>} responseByteArray
   */
  static async sendCommand(messageByteArray, connectionData) {
    const { hostname } = connectionData;
    return new import_WebSocketClientBrowser.WebSocketClientBrowser(hostname).send(messageByteArray);
  }
  /**
   * @async
   * @param {any} configSource
   * @returns {void}
   */
  // eslint-disable-next-line no-unused-vars
  static setConfigSource(configSource) {
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  TransmitterWebsocketBrowser
});
