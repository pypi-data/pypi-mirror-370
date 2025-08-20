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
var RuntimeNameHandler_exports = {};
__export(RuntimeNameHandler_exports, {
  RuntimeNameHandler: () => RuntimeNameHandler
});
module.exports = __toCommonJS(RuntimeNameHandler_exports);
var import_RuntimeName = require("./RuntimeName.cjs");
class RuntimeNameHandler {
  /**
   * @param {number} runtimeName
   * @returns {RuntimeType}
   */
  static getName(runtimeName) {
    switch (runtimeName) {
      case import_RuntimeName.RuntimeName.Clr:
        return "clr";
      case import_RuntimeName.RuntimeName.Go:
        return "go";
      case import_RuntimeName.RuntimeName.Jvm:
        return "jvm";
      case import_RuntimeName.RuntimeName.Netcore:
        return "netcore";
      case import_RuntimeName.RuntimeName.Perl:
        return "perl";
      case import_RuntimeName.RuntimeName.Python:
        return "python";
      case import_RuntimeName.RuntimeName.Ruby:
        return "ruby";
      case import_RuntimeName.RuntimeName.Nodejs:
        return "nodejs";
      case import_RuntimeName.RuntimeName.Cpp:
        return "cpp";
      case import_RuntimeName.RuntimeName.Php:
        return "php";
      case import_RuntimeName.RuntimeName.Python27:
        return "python27";
      default:
        throw new Error("Invalid runtime name.");
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  RuntimeNameHandler
});
