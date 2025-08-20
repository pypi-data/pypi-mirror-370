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
var SetInstanceFieldHandler_exports = {};
__export(SetInstanceFieldHandler_exports, {
  SetInstanceFieldHandler: () => SetInstanceFieldHandler
});
module.exports = __toCommonJS(SetInstanceFieldHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
class SetInstanceFieldHandler extends import_AbstractHandler.AbstractHandler {
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
        throw new Error("Set Instance Field parameters mismatch");
      }
      const { payload } = command;
      let instance = payload[0];
      let field = payload[1];
      let value = payload[2];
      if (typeof instance[field] === "undefined") {
        let fields = Object.keys(instance);
        let message = `Field ${field} not found in object. Available fields:
`;
        fields.forEach((fieldIter) => {
          message += `${fieldIter}
`;
        });
        throw new Error(message);
      }
      instance[field] = value;
      return 0;
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  SetInstanceFieldHandler
});
