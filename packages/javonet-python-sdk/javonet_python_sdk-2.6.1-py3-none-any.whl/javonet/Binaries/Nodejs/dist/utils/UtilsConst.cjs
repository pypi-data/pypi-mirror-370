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
var UtilsConst_exports = {};
__export(UtilsConst_exports, {
  UtilsConst: () => UtilsConst
});
module.exports = __toCommonJS(UtilsConst_exports);
var import_Runtime = require("./Runtime.cjs");
const import_meta = {};
let fs = null;
let path = null;
const requireDynamic = (0, import_Runtime.getRequire)(import_meta.url);
class UtilsConst {
  /** @type {string} */
  static _javonetWorkingDirectory = ".";
  /** @type {string} */
  static _configSource = "";
  /** @type {string} */
  static _licenseKey = "";
  /**
   * @param {string} inputPath
   */
  static setJavonetWorkingDirectory(inputPath) {
    if (!inputPath) {
      return;
    }
    let normalizedPath = inputPath.replace(/\\/g, "/");
    if (!normalizedPath.endsWith("/")) {
      normalizedPath += "/";
    }
    if ((0, import_Runtime.isNodejsRuntime)()) {
      if (!fs) {
        fs = requireDynamic("fs");
      }
      if (!fs.existsSync(normalizedPath)) {
        fs.mkdirSync(normalizedPath, { recursive: true });
        fs.chmodSync(normalizedPath, 448);
      }
    }
    UtilsConst._javonetWorkingDirectory = normalizedPath;
  }
  /**
   * @returns {string}
   */
  static getJavonetWorkingDirectory() {
    if ((0, import_Runtime.isNodejsRuntime)() && !UtilsConst._javonetWorkingDirectory) {
      if (!path) {
        path = requireDynamic("path");
      }
      UtilsConst._javonetWorkingDirectory = path.resolve() + "/";
    }
    return UtilsConst._javonetWorkingDirectory;
  }
  /**
   * @param {string} value
   */
  static setConfigSource(value) {
    UtilsConst._configSource = value;
  }
  /**
   * @returns {string}
   */
  static getConfigSource() {
    return UtilsConst._configSource;
  }
  /**
   * @param {string} value
   */
  static setLicenseKey(value) {
    if (!value || value === "your-license-key") {
      return;
    }
    UtilsConst._licenseKey = value;
  }
  /**
   * @returns {string}
   */
  static getLicenseKey() {
    return UtilsConst._licenseKey;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  UtilsConst
});
