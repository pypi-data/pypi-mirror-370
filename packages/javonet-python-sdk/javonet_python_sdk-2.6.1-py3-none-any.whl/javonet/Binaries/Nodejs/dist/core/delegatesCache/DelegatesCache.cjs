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
var DelegatesCache_exports = {};
__export(DelegatesCache_exports, {
  delegatesCacheInstance: () => delegatesCacheInstance
});
module.exports = __toCommonJS(DelegatesCache_exports);
var import_generateGuid = require("../../utils/guid/generateGuid.cjs");
class DelegatesCache {
  cache = /* @__PURE__ */ new Map();
  /**
   * Adds a delegate to the cache and returns its unique ID.
   * @param {Function} delegateInstance - The delegate function to store.
   * @returns {string} The unique ID for the delegate.
   */
  addDelegate(delegateInstance) {
    const delegateId = (0, import_generateGuid.generateGUID)();
    this.cache.set(delegateId, delegateInstance);
    return delegateId;
  }
  /**
   * Retrieves a delegate by its unique ID.
   * @param {string} delegateId - The unique ID of the delegate.
   * @returns {Function} The delegate function.
   * @throws {Error} If the delegate is not found.
   */
  getDelegate(delegateId) {
    const delegateInstance = this.cache.get(delegateId);
    if (!delegateInstance) {
      throw new Error("Delegate not found");
    }
    return delegateInstance;
  }
}
const delegatesCacheInstance = new DelegatesCache();
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  delegatesCacheInstance
});
