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
var GetInstanceFieldHandler_exports = {};
__export(GetInstanceFieldHandler_exports, {
  GetInstanceFieldHandler: () => GetInstanceFieldHandler
});
module.exports = __toCommonJS(GetInstanceFieldHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
class GetInstanceFieldHandler extends import_AbstractHandler.AbstractHandler {
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
        throw new Error("Get Instance Field parameters mismatch");
      }
      const { payload } = command;
      let instance = payload[0];
      let field = payload[1];
      let instanceField = instance[field];
      if (typeof instanceField === "undefined") {
        let fields = Object.keys(instance);
        let message = `Field ${field} not found in object. Available fields:
`;
        fields.forEach((fieldIter) => {
          message += `${fieldIter}
`;
        });
        throw new Error(message);
      } else {
        return instanceField;
      }
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  GetInstanceFieldHandler
});
