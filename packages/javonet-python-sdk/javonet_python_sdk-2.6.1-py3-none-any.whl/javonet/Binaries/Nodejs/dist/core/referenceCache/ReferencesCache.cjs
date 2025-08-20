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
var ReferencesCache_exports = {};
__export(ReferencesCache_exports, {
  ReferencesCache: () => ReferencesCache
});
module.exports = __toCommonJS(ReferencesCache_exports);
var import_v4 = require("../../utils/nodejs/uuid/v4.cjs");
let _cache = {};
let _instance = null;
class ReferencesCache {
  /**
   * @returns {ReferencesCache}
   */
  static getInstance() {
    if (_instance === null) {
      _instance = new ReferencesCache();
    }
    return _instance;
  }
  /**
   * @param {any} reference
   * @returns {string}
   */
  cacheReference(reference) {
    let id = (0, import_v4.v4)();
    _cache[id] = reference;
    return id;
  }
  /**
   * @param {string} id
   * @returns {any}
   */
  resolveReference(id) {
    return _cache[id];
  }
  /**
   * @param {string} id
   * @returns {number}
   */
  deleteReference(id) {
    delete _cache[id];
    return 0;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ReferencesCache
});
