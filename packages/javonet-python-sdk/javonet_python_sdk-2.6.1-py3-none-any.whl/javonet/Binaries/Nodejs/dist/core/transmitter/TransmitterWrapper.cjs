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
var TransmitterWrapper_exports = {};
__export(TransmitterWrapper_exports, {
  TransmitterWrapper: () => TransmitterWrapper
});
module.exports = __toCommonJS(TransmitterWrapper_exports);
var import_Runtime = require("../../utils/Runtime.cjs");
var import_ReceiverNative = require("../receiver/ReceiverNative.cjs");
const import_meta = {};
let library = null;
let path = null;
const requireDynamic = (0, import_Runtime.getRequire)(import_meta.url);
class TransmitterWrapper {
  static isNativeLibraryLoaded() {
    return Boolean(library);
  }
  static loadNativeLibrary() {
    if (!(0, import_Runtime.isNodejsRuntime)()) {
      throw new Error("Javonet.loadNativeLibrary is not supported in this runtime");
    }
    if (this.isNativeLibraryLoaded()) {
      return;
    }
    try {
      if (!path) {
        path = requireDynamic("path");
      }
      const packagePath = (0, import_Runtime.getDependency)("javonet-binaries", import_meta.url);
      const binariesRootPath = path.dirname(packagePath);
      const nativeAddonPath = path.join(
        binariesRootPath,
        "build",
        "Release",
        "JavonetNodejsRuntimeAddon.node"
      );
      library = requireDynamic(nativeAddonPath);
      library.initializeTransmitter(binariesRootPath);
      library.setReceiverNative(global?.ReceiverNative);
    } catch (error) {
      throw error;
    }
  }
  /**
   * @param {string} licenseKey
   */
  static activate(licenseKey) {
    this.loadNativeLibrary();
    return library.activate(licenseKey);
  }
  /**
   * @param {Int8Array} messageArray
   */
  static sendCommand(messageArray) {
    this.loadNativeLibrary();
    return library.sendCommand(messageArray);
  }
  /**
   * @param {string} configSource
   */
  static setConfigSource(configSource) {
    this.loadNativeLibrary();
    return library.setConfigSource(configSource);
  }
  /**
   * @param {string} path
   */
  static setJavonetWorkingDirectory(path2) {
    this.loadNativeLibrary();
    library.setJavonetWorkingDirectory(path2);
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  TransmitterWrapper
});
