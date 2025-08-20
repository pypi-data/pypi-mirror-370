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
var ArrayGetItemHandler_exports = {};
__export(ArrayGetItemHandler_exports, {
  ArrayGetItemHandler: () => ArrayGetItemHandler
});
module.exports = __toCommonJS(ArrayGetItemHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
class ArrayGetItemHandler extends import_AbstractHandler.AbstractHandler {
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
        throw new Error("Array Get Item parameters mismatch");
      }
      let array = command.payload[0];
      let indexes;
      if (Array.isArray(command.payload[1])) {
        indexes = command.payload[1];
      } else {
        indexes = command.payload.slice(1);
      }
      if (indexes.length === 1) {
        return array[indexes[0]];
      } else {
        let array_copy = [...array];
        for (let i = 0; i < indexes.length; i++) {
          array_copy = array_copy[indexes[i]];
        }
        return array_copy;
      }
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ArrayGetItemHandler
});
