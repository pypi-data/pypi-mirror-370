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
var CreateClassInstanceHandler_exports = {};
__export(CreateClassInstanceHandler_exports, {
  CreateClassInstanceHandler: () => CreateClassInstanceHandler
});
module.exports = __toCommonJS(CreateClassInstanceHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
class CreateClassInstanceHandler extends import_AbstractHandler.AbstractHandler {
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
        throw new Error("Create Class Instance parameters mismatch");
      }
      let clazz = command.payload[0];
      let constructorArguments = command.payload.slice(1);
      let instance = new clazz(...constructorArguments);
      if (typeof instance === "undefined") {
        let methods = Object.getOwnPropertyNames(clazz).filter(function(property) {
          return typeof clazz[property] === "function";
        });
        let message = `Method 'constructor' not found in class. Available methods:
`;
        methods.forEach((methodIter) => {
          message += `${methodIter}
`;
        });
        throw new Error(message);
      } else {
        return instance;
      }
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  CreateClassInstanceHandler
});
