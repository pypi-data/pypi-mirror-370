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
var InvokeGlobalFunctionHandler_exports = {};
__export(InvokeGlobalFunctionHandler_exports, {
  InvokeGlobalFunctionHandler: () => InvokeGlobalFunctionHandler
});
module.exports = __toCommonJS(InvokeGlobalFunctionHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
class InvokeGlobalFunctionHandler extends import_AbstractHandler.AbstractHandler {
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
        throw new Error("Invoke Global Function parameters mismatch");
      }
      const { payload } = command;
      const functionName = payload[0];
      const args = payload.slice(1);
      if (typeof global[functionName] === "function") {
        return Reflect.apply(global[functionName], void 0, args);
      } else {
        let methods = Object.getOwnPropertyNames(global).filter(function(property) {
          return typeof global[property] === "function";
        });
        let message = `Method ${functionName} not found in global. Available methods:
`;
        methods.forEach((methodIter) => {
          message += `${methodIter}
`;
        });
        throw new Error(message);
      }
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  InvokeGlobalFunctionHandler
});
