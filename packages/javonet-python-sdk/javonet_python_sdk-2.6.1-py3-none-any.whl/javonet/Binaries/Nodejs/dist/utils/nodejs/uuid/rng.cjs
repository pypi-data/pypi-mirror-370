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
var rng_exports = {};
__export(rng_exports, {
  rng: () => rng
});
module.exports = __toCommonJS(rng_exports);
var import_Runtime = require("../../Runtime.cjs");
const import_meta = {};
const requireDynamic = (0, import_Runtime.getRequire)(import_meta.url);
const rnds8Pool = new Uint8Array(256);
let poolPtr = rnds8Pool.length;
function rng() {
  try {
    const crypto = requireDynamic("crypto");
    if (poolPtr > rnds8Pool.length - 16) {
      crypto.randomFillSync(rnds8Pool);
      poolPtr = 0;
    }
    return rnds8Pool.slice(poolPtr, poolPtr += 16);
  } catch (error) {
    if (error.code === "MODULE_NOT_FOUND") {
      throw new Error("crypto module not found. Please install it using npm install crypto");
    }
    throw error;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  rng
});
