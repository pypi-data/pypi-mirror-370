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
var Receiver_exports = {};
__export(Receiver_exports, {
  Receiver: () => Receiver
});
module.exports = __toCommonJS(Receiver_exports);
var import_Interpreter = require("../interpreter/Interpreter.cjs");
var import_CommandSerializer = require("../protocol/CommandSerializer.cjs");
var import_Runtime = require("../../utils/Runtime.cjs");
var import_InMemoryConnectionData = require("../../utils/connectionData/InMemoryConnectionData.cjs");
var import_ExceptionSerializer = require("../../utils/exception/ExceptionSerializer.cjs");
var import_Command = require("../../utils/Command.cjs");
var import_CommandType = require("../../utils/CommandType.cjs");
var import_RuntimeName = require("../../utils/RuntimeName.cjs");
var import_RuntimeLogger = require("../../utils/RuntimeLogger.cjs");
class Receiver {
  static connectionData = new import_InMemoryConnectionData.InMemoryConnectionData();
  Receiver() {
  }
  static getRuntimeInfo() {
    return import_RuntimeLogger.RuntimeLogger.getRuntimeInfo();
  }
  /**
   * @param {Int8Array} messageByteArray
   */
  static sendCommand(messageByteArray) {
    try {
      return new import_CommandSerializer.CommandSerializer().serialize(
        new import_Interpreter.Interpreter().process(messageByteArray),
        this.connectionData
      );
    } catch (error) {
      const exceptionCommand = import_ExceptionSerializer.ExceptionSerializer.serializeException(
        error,
        new import_Command.Command(import_RuntimeName.RuntimeName.Nodejs, import_CommandType.CommandType.Exception, [])
      );
      return new import_CommandSerializer.CommandSerializer().serialize(exceptionCommand, this.connectionData);
    }
  }
  /**
   * @param {Int8Array} messageByteArray
   * @returns {Int8Array}
   */
  static heartBeat(messageByteArray) {
    let response = new Int8Array(2);
    response[0] = messageByteArray[11];
    response[1] = messageByteArray[12] - 2;
    return response;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  Receiver
});
