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
var ResolveReferenceHandler_exports = {};
__export(ResolveReferenceHandler_exports, {
  ResolveReferenceHandler: () => ResolveReferenceHandler
});
module.exports = __toCommonJS(ResolveReferenceHandler_exports);
var import_ReferencesCache = require("../referenceCache/ReferencesCache.cjs");
var import_AbstractHandler = require("./AbstractHandler.cjs");
var import_CommandType = require("../../utils/CommandType.cjs");
var import_RuntimeName = require("../../utils/RuntimeName.cjs");
var import_Command = require("../../utils/Command.cjs");
class ResolveReferenceHandler extends import_AbstractHandler.AbstractHandler {
  constructor() {
    super();
  }
  /**
   * @param {Command} command
   * @returns {any}
   */
  process(command) {
    if (command.runtimeName === import_RuntimeName.RuntimeName.Nodejs) {
      return import_ReferencesCache.ReferencesCache.getInstance().resolveReference(command.payload[0]);
    } else {
      return new import_Command.Command(command.runtimeName, import_CommandType.CommandType.Reference, command.payload[0]);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ResolveReferenceHandler
});
