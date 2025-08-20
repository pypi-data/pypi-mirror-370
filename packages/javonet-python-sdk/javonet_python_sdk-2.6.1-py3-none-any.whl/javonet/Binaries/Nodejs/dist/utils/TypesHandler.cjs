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
var TypesHandler_exports = {};
__export(TypesHandler_exports, {
  TypesHandler: () => TypesHandler
});
module.exports = __toCommonJS(TypesHandler_exports);
class TypesHandler {
  /**
   * Converts a JavaScript type to a JType equivalent.
   * @param {Function} type - The JavaScript type.
   * @returns {string} The corresponding type name
   */
  static convertTypeToJType(type) {
    switch (type) {
      case Boolean:
        return "JType.Boolean";
      case Number:
        return "JType.Float";
      case String:
        return "JType.String";
      case Object:
        return typeof type;
      default:
        return typeof type;
    }
  }
  /**
   * @param {unknown} value
   * @returns {boolean}
   */
  static isPrimitiveOrNullOrUndefined(value) {
    return value === null || value === void 0 || typeof value === "string" || typeof value === "number" || typeof value === "boolean";
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  TypesHandler
});
