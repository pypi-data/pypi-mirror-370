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
var InvokeDelegateHandler_exports = {};
__export(InvokeDelegateHandler_exports, {
  InvokeDelegateHandler: () => InvokeDelegateHandler
});
module.exports = __toCommonJS(InvokeDelegateHandler_exports);
var import_DelegatesCache = require("../delegatesCache/DelegatesCache.cjs");
var import_AbstractHandler = require("./AbstractHandler.cjs");
class InvokeDelegateHandler extends import_AbstractHandler.AbstractHandler {
  constructor() {
    super();
    this.requiredParametersCount = 1;
  }
  /**
   * Processes a command to invoke a delegate.
   * @param {Command} command - The command containing payload data.
   * @returns {*} The result of the delegate invocation.
   * @throws {Error} If the parameters mismatch or the delegate cannot be found.
   */
  process(command) {
    const payload = command.payload;
    if (payload.length < this.requiredParametersCount) {
      throw new Error(`${this.constructor.name} parameters mismatch`);
    }
    const guid = payload[0];
    const delegate = import_DelegatesCache.delegatesCacheInstance.getDelegate(guid);
    if (!delegate) {
      throw new Error("Delegate not found in cache");
    }
    return delegate;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  InvokeDelegateHandler
});
