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
var SetGlobalStaticFieldHandler_exports = {};
__export(SetGlobalStaticFieldHandler_exports, {
  SetGlobalStaticFieldHandler: () => SetGlobalStaticFieldHandler
});
module.exports = __toCommonJS(SetGlobalStaticFieldHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
class SetGlobalStaticFieldHandler extends import_AbstractHandler.AbstractHandler {
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
        throw new Error("Set gloabal static field parameters mismatch");
      }
      const { payload } = command;
      const splitted = payload[0].split(".");
      const value = payload[1];
      let fieldToSet;
      for (let i = 0; i < splitted.length; i++) {
        if (typeof (fieldToSet ? fieldToSet[splitted[i]] : global[splitted[i]]) === "undefined") {
          let fields = Object.keys(fieldToSet ? fieldToSet : global);
          let message = `Field ${splitted[i]} not found in object. Available fields:
`;
          fields.forEach((fieldIter) => {
            message += `${fieldIter}
`;
          });
          throw new Error(message);
        }
        fieldToSet = !fieldToSet ? global[splitted[i]] : fieldToSet[splitted[i]];
      }
      fieldToSet = value;
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  SetGlobalStaticFieldHandler
});
