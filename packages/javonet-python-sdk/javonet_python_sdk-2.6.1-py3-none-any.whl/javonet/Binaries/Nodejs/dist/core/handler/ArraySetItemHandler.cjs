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
var ArraySetItemHandler_exports = {};
__export(ArraySetItemHandler_exports, {
  ArraySetItemHandler: () => ArraySetItemHandler
});
module.exports = __toCommonJS(ArraySetItemHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
class ArraySetItemHandler extends import_AbstractHandler.AbstractHandler {
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
        throw new Error("Array Set Item parameters mismatch");
      }
      let array = command.payload[0];
      let value = command.payload[2];
      let indexes;
      if (Array.isArray(command.payload[1])) {
        indexes = command.payload[1];
      } else {
        indexes = [command.payload[1]];
      }
      if (indexes.length === 1) {
        array[indexes[0]] = value;
      } else {
        for (let i = 0; i < indexes.length - 1; i++) {
          array = array[indexes[i]];
        }
        array[indexes[indexes.length - 1]] = value;
      }
      return 0;
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ArraySetItemHandler
});
