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
var CastingHandler_exports = {};
__export(CastingHandler_exports, {
  CastingHandler: () => CastingHandler
});
module.exports = __toCommonJS(CastingHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
class CastingHandler extends import_AbstractHandler.AbstractHandler {
  /**
   * @param {Command} command
   */
  process(command) {
    throw new Error(`Dynamically typed languages are not supporting casting`);
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  CastingHandler
});
