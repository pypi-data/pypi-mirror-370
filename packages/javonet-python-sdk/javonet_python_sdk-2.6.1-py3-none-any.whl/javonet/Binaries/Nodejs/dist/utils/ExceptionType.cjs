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
var ExceptionType_exports = {};
__export(ExceptionType_exports, {
  ExceptionType: () => ExceptionType
});
module.exports = __toCommonJS(ExceptionType_exports);
const ExceptionType = (
  /** @type {const} */
  {
    EXCEPTION: 0,
    IO_EXCEPTION: 1,
    FILE_NOT_FOUND_EXCEPTION: 2,
    RUNTIME_EXCEPTION: 3,
    ARITHMETIC_EXCEPTION: 4,
    ILLEGAL_ARGUMENT_EXCEPTION: 5,
    INDEX_OUT_OF_BOUNDS_EXCEPTION: 6,
    NULL_POINTER_EXCEPTION: 7
  }
);
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ExceptionType
});
