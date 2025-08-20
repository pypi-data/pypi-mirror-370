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
var InvokeInstanceMethodHandler_exports = {};
__export(InvokeInstanceMethodHandler_exports, {
  InvokeInstanceMethodHandler: () => InvokeInstanceMethodHandler
});
module.exports = __toCommonJS(InvokeInstanceMethodHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
class InvokeInstanceMethodHandler extends import_AbstractHandler.AbstractHandler {
  requiredParametersCount = 2;
  constructor() {
    super();
  }
  /**
   * @param {Command} command
   */
  process(command) {
    try {
      if (command.payload.length < this.requiredParametersCount) {
        throw new Error("Invoke Instance Method parameters mismatch");
      }
      const { payload } = command;
      let instance = payload[0];
      let methodName = payload[1];
      let args = payload.slice(2);
      let method = instance[methodName];
      if (typeof method === "undefined") {
        let methods = Object.getOwnPropertyNames(instance.__proto__).filter(function(property) {
          return typeof instance.__proto__[property] === "function";
        });
        let message = `Method ${methodName} not found in object. Available methods:
`;
        methods.forEach((methodIter) => {
          message += `${methodIter}
`;
        });
        throw new Error(message);
      } else {
        return Reflect.apply(method, instance, args);
      }
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  InvokeInstanceMethodHandler
});
