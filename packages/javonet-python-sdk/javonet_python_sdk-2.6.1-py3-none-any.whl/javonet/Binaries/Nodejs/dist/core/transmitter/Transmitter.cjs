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
var Transmitter_exports = {};
__export(Transmitter_exports, {
  Transmitter: () => Transmitter
});
module.exports = __toCommonJS(Transmitter_exports);
var import_TransmitterWrapper = require("./TransmitterWrapper.cjs");
class Transmitter {
  /**
   * @param {Int8Array} messageArray
   * @returns {Int8Array}
   */
  static sendCommand(messageArray) {
    return import_TransmitterWrapper.TransmitterWrapper.sendCommand(messageArray);
  }
  /**
   * @param {string} licenseKey 
   * @returns {void}
   */
  static activate(licenseKey) {
    return import_TransmitterWrapper.TransmitterWrapper.activate(licenseKey);
  }
  /**
   * @param {string} configSource
   * @returns {void}
  */
  static setConfigSource(configSource) {
    return import_TransmitterWrapper.TransmitterWrapper.setConfigSource(configSource);
  }
  /**
   * @param {string} workingDirectory 
   * @returns 
   */
  static setJavonetWorkingDirectory(workingDirectory) {
    return import_TransmitterWrapper.TransmitterWrapper.setJavonetWorkingDirectory(workingDirectory);
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  Transmitter
});
