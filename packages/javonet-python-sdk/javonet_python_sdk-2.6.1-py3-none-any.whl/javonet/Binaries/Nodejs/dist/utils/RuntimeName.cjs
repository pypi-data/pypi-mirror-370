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
var RuntimeName_exports = {};
__export(RuntimeName_exports, {
  RuntimeName: () => RuntimeName
});
module.exports = __toCommonJS(RuntimeName_exports);
const RuntimeName = (
  /** @type {const} */
  {
    Clr: 0,
    Go: 1,
    Jvm: 2,
    Netcore: 3,
    Perl: 4,
    Python: 5,
    Ruby: 6,
    Nodejs: 7,
    Cpp: 8,
    Php: 9,
    Python27: 10
  }
);
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  RuntimeName
});
