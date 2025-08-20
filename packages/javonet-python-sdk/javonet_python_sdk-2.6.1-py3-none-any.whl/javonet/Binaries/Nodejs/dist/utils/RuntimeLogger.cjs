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
var RuntimeLogger_exports = {};
__export(RuntimeLogger_exports, {
  RuntimeLogger: () => RuntimeLogger
});
module.exports = __toCommonJS(RuntimeLogger_exports);
var import_Runtime = require("./Runtime.cjs");
const import_meta = {};
let os = null;
let process = null;
const requireDynamic = (0, import_Runtime.getRequire)(import_meta.url);
if ((0, import_Runtime.isNodejsRuntime)()) {
  try {
    os = requireDynamic("os");
    process = requireDynamic("process");
  } catch (error) {
    throw error;
  }
}
class RuntimeLogger {
  static notLoggedYet = true;
  static getRuntimeInfo() {
    try {
      return `JavaScript Managed Runtime Info:
Node.js Version: ${process?.version}
OS Version: ${os?.type()} ${os?.release()}
Process Architecture: ${os?.arch()}
Current Directory: ${process?.cwd()}
`;
    } catch (e) {
      return "JavaScript Managed Runtime Info: Error while fetching runtime info";
    }
  }
  static printRuntimeInfo() {
    if (this.notLoggedYet) {
      console.log(this.getRuntimeInfo());
      this.notLoggedYet = false;
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  RuntimeLogger
});
