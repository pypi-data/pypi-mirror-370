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
var Interpreter_exports = {};
__export(Interpreter_exports, {
  Interpreter: () => Interpreter
});
module.exports = __toCommonJS(Interpreter_exports);
var import_ConnectionType = require("../../utils/ConnectionType.cjs");
var import_Runtime = require("../../utils/Runtime.cjs");
var import_RuntimeName = require("../../utils/RuntimeName.cjs");
var import_CommandDeserializer = require("../protocol/CommandDeserializer.cjs");
var import_CommandSerializer = require("../protocol/CommandSerializer.cjs");
var import_TransmitterWebsocketBrowser = require("../transmitter/TransmitterWebsocketBrowser.cjs");
var import_TransmitterWebsocket = require("../transmitter/TransmitterWebsocket.cjs");
var import_Handler = require("../handler/Handler.cjs");
const import_meta = {};
let _Receiver = null;
let _Transmitter = null;
let _TransmitterWebsocket = null;
if (!_TransmitterWebsocket) {
  _TransmitterWebsocket = (0, import_Runtime.isNodejsRuntime)() ? import_TransmitterWebsocket.TransmitterWebsocket : import_TransmitterWebsocketBrowser.TransmitterWebsocketBrowser;
}
const requireDynamic = (0, import_Runtime.getRequire)(import_meta.url);
class Interpreter {
  /** @type {Handler | null} */
  _handler = null;
  /** @type {Handler} */
  get handler() {
    if (!this._handler) {
      this._handler = new import_Handler.Handler(this);
    }
    return this._handler;
  }
  /**
   *
   * @param {Command} command
   * @param {IConnectionData} connectionData
   * @returns
   */
  async executeAsync(command, connectionData) {
    try {
      let messageByteArray = new import_CommandSerializer.CommandSerializer().serialize(command, connectionData);
      let responseByteArray = void 0;
      if (connectionData.connectionType === import_ConnectionType.ConnectionType.WEB_SOCKET) {
        const _response = await _TransmitterWebsocket?.sendCommand(messageByteArray, connectionData);
        if (_response) {
          const command2 = new import_CommandDeserializer.CommandDeserializer(_response).deserialize();
          return command2;
        } else {
          throw new Error("Response not received from TransmitterWebsocket");
        }
      } else {
        if (!(0, import_Runtime.isNodejsRuntime)()) {
          throw new Error("InMemory is only allowed in Nodejs runtime");
        }
        if (command.runtimeName === import_RuntimeName.RuntimeName.Nodejs) {
          if (!_Receiver) {
            const { Receiver } = require("../receiver/Receiver.cjs");
            _Receiver = Receiver;
          }
          responseByteArray = await _Receiver?.sendCommand(messageByteArray);
        } else {
          if (!_Transmitter) {
            const { Transmitter } = require("../transmitter/Transmitter.cjs");
            _Transmitter = Transmitter;
          }
          responseByteArray = await _Transmitter?.sendCommand(messageByteArray);
        }
      }
      if (!responseByteArray) {
        throw new Error("No response received from Transmitter");
      }
      return new import_CommandDeserializer.CommandDeserializer(responseByteArray).deserialize();
    } catch (error) {
      throw error;
    }
  }
  /**
   *
   * @param {Command} command
   * @param {IConnectionData} connectionData
   * @returns {Command | Promise<Command>}
   */
  execute(command, connectionData) {
    try {
      let messageByteArray = new import_CommandSerializer.CommandSerializer().serialize(command, connectionData);
      let responseByteArray = void 0;
      if (connectionData.connectionType === import_ConnectionType.ConnectionType.WEB_SOCKET) {
        throw new Error("Not supported");
      }
      if (connectionData.connectionType === import_ConnectionType.ConnectionType.IN_MEMORY) {
        if (!(0, import_Runtime.isNodejsRuntime)()) {
          throw new Error("InMemory is only allowed in Nodejs runtime");
        }
        if (command.runtimeName === import_RuntimeName.RuntimeName.Nodejs) {
          if (!_Receiver) {
            const { Receiver } = require("../receiver/Receiver.cjs");
            _Receiver = Receiver;
          }
          responseByteArray = _Receiver?.sendCommand(messageByteArray);
        } else {
          if (!_Transmitter) {
            const { Transmitter } = require("../transmitter/Transmitter.cjs");
            _Transmitter = Transmitter;
          }
          responseByteArray = _Transmitter?.sendCommand(messageByteArray);
        }
      }
      if (!responseByteArray) {
        throw new Error("No response received from Transmitter");
      }
      return new import_CommandDeserializer.CommandDeserializer(responseByteArray).deserialize();
    } catch (error) {
      throw error;
    }
  }
  /**
   *
   * @param {Int8Array} messageByteArray
   * @returns {Command}
   */
  process(messageByteArray) {
    try {
      const receivedCommand = new import_CommandDeserializer.CommandDeserializer(messageByteArray).deserialize();
      return this.handler?.handleCommand(receivedCommand);
    } catch (error) {
      throw error;
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  Interpreter
});
