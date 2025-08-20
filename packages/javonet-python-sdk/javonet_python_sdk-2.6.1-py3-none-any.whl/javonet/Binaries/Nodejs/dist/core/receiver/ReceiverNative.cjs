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
var ReceiverNative_exports = {};
__export(ReceiverNative_exports, {
  ReceiverNative: () => ReceiverNative
});
module.exports = __toCommonJS(ReceiverNative_exports);
var import_Receiver = require("./Receiver.cjs");
class ReceiverNative {
  /**
   * @param {Int8Array} messageByteArray
   */
  static sendCommand(messageByteArray) {
    return import_Receiver.Receiver.sendCommand(messageByteArray);
  }
  /**
   * @param {Int8Array} messageByteArray
   */
  static heartBeat(messageByteArray) {
    return import_Receiver.Receiver.heartBeat(messageByteArray);
  }
}
global.ReceiverNative = ReceiverNative;
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ReceiverNative
});
