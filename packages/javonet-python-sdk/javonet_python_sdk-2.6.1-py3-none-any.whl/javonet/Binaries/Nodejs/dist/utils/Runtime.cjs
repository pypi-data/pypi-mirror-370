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
var Runtime_exports = {};
__export(Runtime_exports, {
  getDependency: () => getDependency,
  getDirname: () => getDirname,
  getRequire: () => getRequire,
  getRuntimeExtension: () => getRuntimeExtension,
  isBrowserRuntime: () => isBrowserRuntime,
  isEsmRuntime: () => isEsmRuntime,
  isNodejsRuntime: () => isNodejsRuntime
});
module.exports = __toCommonJS(Runtime_exports);
var import_CreateRequire_node = require("./CreateRequire.node.cjs");
const import_meta = {};
let pathToFileURL = null;
let fileURLToPath = null;
let path = null;
function isNodejsRuntime() {
  return typeof process !== "undefined" && process.versions != null && process.versions.node != null;
}
function isBrowserRuntime() {
  return typeof window !== "undefined" && typeof window.document !== "undefined";
}
function isEsmRuntime() {
  return typeof __filename === "undefined";
}
function getRuntimeExtension() {
  return isEsmRuntime() ? "js" : "cjs";
}
const getRequire = (callerPath) => {
  try {
    if (isNodejsRuntime()) {
      if (typeof require !== "undefined") {
        return require;
      }
      if (callerPath === void 0) {
        return (0, import_CreateRequire_node.createRequire)(import_meta.url);
      }
      const baseUrl = callerPath?.startsWith("file:") ? callerPath : pathToFileURL(callerPath).href;
      return (0, import_CreateRequire_node.createRequire)(baseUrl);
    }
    return new Error("Runtime not supported");
  } catch (error) {
    throw error;
  }
};
const getDirname = () => {
  if (isBrowserRuntime()) {
    return new Error("Runtime not supported");
  }
  if (isEsmRuntime()) {
    const __filename2 = fileURLToPath(import_meta.url);
    return path.dirname(__filename2);
  }
  return __dirname;
};
const getDependency = (dependencyName, callerPathOrUrl) => {
  try {
    let baseUrl = callerPathOrUrl;
    if (!baseUrl && typeof __filename !== "undefined") {
      baseUrl = __filename;
    }
    const contextualRequire = getRequire(baseUrl);
    return contextualRequire.resolve(dependencyName);
  } catch (error) {
    throw new Error(
      `Failed to resolve dependency '${dependencyName}' from '${callerPathOrUrl}': ${error.message}`
    );
  }
};
if (isNodejsRuntime()) {
  const requireDynamic = getRequire(import_meta.url);
  if (fileURLToPath === null) {
    fileURLToPath = requireDynamic("url").fileURLToPath;
  }
  if (path === null) {
    path = requireDynamic("path");
  }
  if (pathToFileURL === null) {
    pathToFileURL = requireDynamic("url").pathToFileURL;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  getDependency,
  getDirname,
  getRequire,
  getRuntimeExtension,
  isBrowserRuntime,
  isEsmRuntime,
  isNodejsRuntime
});
