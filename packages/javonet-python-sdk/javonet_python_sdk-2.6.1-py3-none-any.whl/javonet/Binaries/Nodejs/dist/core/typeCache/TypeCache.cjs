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
var TypeCache_exports = {};
__export(TypeCache_exports, {
  TypeCache: () => TypeCache
});
module.exports = __toCommonJS(TypeCache_exports);
class TypeCache {
  /** @type {TypeCache | null} */
  static _instance = null;
  /** @type {string[]} */
  typeCache = [];
  constructor() {
    if (TypeCache._instance === null) {
      TypeCache._instance = this;
    }
    return TypeCache._instance;
  }
  /**
   * @param {string} typRegex
   */
  cacheType(typRegex) {
    this.typeCache.push(typRegex);
  }
  isTypeCacheEmpty() {
    return this.typeCache.length === 0;
  }
  /**
   * @param {{ name: string }} typeToCheck
   */
  isTypeAllowed(typeToCheck) {
    for (let pattern of this.typeCache) {
      if (new RegExp(pattern).test(typeToCheck.name)) {
        return true;
      }
    }
    return false;
  }
  getCachedTypes() {
    return this.typeCache;
  }
  clearCache() {
    this.typeCache = [];
    return 0;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  TypeCache
});
