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
var DestructReferenceHandler_exports = {};
__export(DestructReferenceHandler_exports, {
  DestructReferenceHandler: () => DestructReferenceHandler
});
module.exports = __toCommonJS(DestructReferenceHandler_exports);
var import_ReferencesCache = require("../referenceCache/ReferencesCache.cjs");
var import_AbstractHandler = require("./AbstractHandler.cjs");
class DestructReferenceHandler extends import_AbstractHandler.AbstractHandler {
  constructor() {
    super();
  }
  /**
   * @param {Command} command
   */
  process(command) {
    try {
      let cache = import_ReferencesCache.ReferencesCache.getInstance();
      return cache.deleteReference(command.payload[0]);
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  DestructReferenceHandler
});
