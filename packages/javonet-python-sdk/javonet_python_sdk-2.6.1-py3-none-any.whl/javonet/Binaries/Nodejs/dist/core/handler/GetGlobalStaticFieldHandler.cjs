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
var GetGlobalStaticFieldHandler_exports = {};
__export(GetGlobalStaticFieldHandler_exports, {
  GetGlobalStaticFieldHandler: () => GetGlobalStaticFieldHandler
});
module.exports = __toCommonJS(GetGlobalStaticFieldHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
class GetGlobalStaticFieldHandler extends import_AbstractHandler.AbstractHandler {
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
        throw new Error("Get global static field parameters mismatch");
      }
      const { payload } = command;
      const splitted = payload[0].split(".");
      let fieldToGet;
      for (let i = 0; i < splitted.length; i++) {
        fieldToGet = !fieldToGet ? global[splitted[i]] : fieldToGet[splitted[i]];
        if (typeof fieldToGet === "undefined") {
          let fields = Object.keys(global);
          let message = `Field ${payload[0]} not found in global. Available fields:
`;
          fields.forEach((fieldIter) => {
            message += `${fieldIter}
`;
          });
          throw new Error(message);
        }
      }
      return fieldToGet;
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  GetGlobalStaticFieldHandler
});
