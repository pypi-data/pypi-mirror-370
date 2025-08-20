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
var Type_exports = {};
__export(Type_exports, {
  Type: () => Type
});
module.exports = __toCommonJS(Type_exports);
const Type = (
  /** @type {const} */
  {
    JAVONET_COMMAND: 0,
    JAVONET_STRING: 1,
    JAVONET_INTEGER: 2,
    JAVONET_BOOLEAN: 3,
    JAVONET_FLOAT: 4,
    JAVONET_BYTE: 5,
    JAVONET_CHAR: 6,
    JAVONET_LONG_LONG: 7,
    JAVONET_DOUBLE: 8,
    JAVONET_UNSIGNED_LONG_LONG: 9,
    JAVONET_UNSIGNED_INTEGER: 10,
    JAVONET_NULL: 11,
    JAVONET_VOID: 12
  }
);
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  Type
});
