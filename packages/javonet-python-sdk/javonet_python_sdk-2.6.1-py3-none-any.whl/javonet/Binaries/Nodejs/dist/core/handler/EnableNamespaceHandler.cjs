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
var EnableNamespaceHandler_exports = {};
__export(EnableNamespaceHandler_exports, {
  EnableNamespaceHandler: () => EnableNamespaceHandler
});
module.exports = __toCommonJS(EnableNamespaceHandler_exports);
var import_NamespaceCache = require("../namespaceCache/NamespaceCache.cjs");
var import_AbstractHandler = require("./AbstractHandler.cjs");
class EnableNamespaceHandler extends import_AbstractHandler.AbstractHandler {
  constructor() {
    super();
    this.requiredParametersCount = 1;
  }
  /**
   * @param {Command} command
   */
  process(command) {
    try {
      if (command.payload.length < this.requiredParametersCount) {
        throw new Error(this.constructor.name + " parameters mismatch");
      }
      const namespace_cache = new import_NamespaceCache.NamespaceCache();
      for (let payload of command.payload) {
        if (typeof payload === "string") {
          namespace_cache.cacheNamespace(payload);
        }
        if (Array.isArray(payload)) {
          for (let namespace_to_enable of payload) {
            namespace_cache.cacheNamespace(namespace_to_enable);
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
  EnableNamespaceHandler
});
