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
var SetStaticFieldHandler_exports = {};
__export(SetStaticFieldHandler_exports, {
  SetStaticFieldHandler: () => SetStaticFieldHandler
});
module.exports = __toCommonJS(SetStaticFieldHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
class SetStaticFieldHandler extends import_AbstractHandler.AbstractHandler {
  requiredParametersCount = 3;
  constructor() {
    super();
  }
  /**
   * @param {Command} command
   */
  process(command) {
    try {
      if (command.payload.length < this.requiredParametersCount) {
        throw new Error("Set static field parameters mismatch");
      }
      const { payload } = command;
      let [obj, field, value] = payload;
      if (typeof obj[field] === "undefined") {
        let fields = Object.keys(obj);
        let message = `Field ${field} not found in class ${obj.constructor.name}. Available fields:
`;
        fields.forEach((fieldIter) => {
          message += `${fieldIter}
`;
        });
        throw new Error(message);
      }
      obj[field] = value;
      return 0;
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  SetStaticFieldHandler
});
