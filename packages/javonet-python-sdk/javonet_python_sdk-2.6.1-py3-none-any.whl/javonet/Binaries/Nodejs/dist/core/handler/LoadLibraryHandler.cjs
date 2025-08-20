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
var LoadLibraryHandler_exports = {};
__export(LoadLibraryHandler_exports, {
  LoadLibraryHandler: () => LoadLibraryHandler
});
module.exports = __toCommonJS(LoadLibraryHandler_exports);
var import_Runtime = require("../../utils/Runtime.cjs");
var import_AbstractHandler = require("./AbstractHandler.cjs");
const import_meta = {};
const dynamicImport = (0, import_Runtime.getRequire)(import_meta.url);
class LoadLibraryHandler extends import_AbstractHandler.AbstractHandler {
  requiredParametersCount = 1;
  /** @type {string[]} */
  static loadedLibraries = [];
  constructor() {
    super();
  }
  /**
   * @param {Command} command
   */
  process(command) {
    if (command.payload.length < this.requiredParametersCount) {
      throw new Error("Load Library parameters mismatch");
    }
    let { payload } = command;
    let [lib] = payload;
    let pathArray = lib.split(/[/\\]/);
    let libraryName = pathArray.length > 1 ? pathArray[pathArray.length - 1] : pathArray[0];
    libraryName = libraryName.replace(".js", "");
    let moduleExports;
    try {
      moduleExports = dynamicImport(lib);
      LoadLibraryHandler.loadedLibraries.push(lib);
    } catch (error) {
      try {
        const modulePath = `${process.cwd()}/${lib}`;
        moduleExports = dynamicImport(modulePath);
      } catch (error2) {
        throw this.process_stack_trace(error2, this.constructor.name);
      }
    }
    global[libraryName] = moduleExports;
    for (const [key, value] of Object.entries(moduleExports)) {
      global[key] = value;
    }
    return 0;
  }
  getLoadedLibraries() {
    return LoadLibraryHandler.loadedLibraries;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  LoadLibraryHandler
});
