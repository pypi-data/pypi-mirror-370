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
var EnableTypeHandler_exports = {};
__export(EnableTypeHandler_exports, {
  EnableTypeHandler: () => EnableTypeHandler
});
module.exports = __toCommonJS(EnableTypeHandler_exports);
var import_TypeCache = require("../typeCache/TypeCache.cjs");
var import_AbstractHandler = require("./AbstractHandler.cjs");
class EnableTypeHandler extends import_AbstractHandler.AbstractHandler {
  requiredParametersCount = 1;
  constructor() {
    super();
  }
  /**
   * @param {Command} command
   */
  process(command) {
    try {
      if (command.payload.length < this.requiredParametersCount) {
        throw new Error("Get Type parameters mismatch");
      }
      const typeCache = new import_TypeCache.TypeCache();
      for (let payload of command.payload) {
        if (typeof payload === "string") {
          typeCache.cacheType(payload);
        }
        if (Array.isArray(payload)) {
          for (let namespace_to_enable of payload) {
            typeCache.cacheType(namespace_to_enable);
          }
        }
      }
      return 0;
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  EnableTypeHandler
});
