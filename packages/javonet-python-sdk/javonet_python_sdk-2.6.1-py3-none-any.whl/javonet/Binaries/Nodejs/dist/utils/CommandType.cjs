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
var CommandType_exports = {};
__export(CommandType_exports, {
  CommandType: () => CommandType
});
module.exports = __toCommonJS(CommandType_exports);
const CommandType = (
  /** @type {const} */
  {
    Value: 0,
    LoadLibrary: 1,
    InvokeStaticMethod: 2,
    GetStaticField: 3,
    SetStaticField: 4,
    CreateClassInstance: 5,
    GetType: 6,
    Reference: 7,
    GetModule: 8,
    InvokeInstanceMethod: 9,
    Exception: 10,
    HeartBeat: 11,
    Cast: 12,
    GetInstanceField: 13,
    Optimize: 14,
    GenerateLib: 15,
    InvokeGlobalFunction: 16,
    DestructReference: 17,
    ArrayReference: 18,
    ArrayGetItem: 19,
    ArrayGetSize: 20,
    ArrayGetRank: 21,
    ArraySetItem: 22,
    Array: 23,
    RetrieveArray: 24,
    SetInstanceField: 25,
    InvokeGenericStaticMethod: 26,
    InvokeGenericMethod: 27,
    GetEnumItem: 28,
    GetEnumName: 29,
    GetEnumValue: 30,
    AsRef: 31,
    AsOut: 32,
    GetRefValue: 33,
    EnableNamespace: 34,
    EnableType: 35,
    CreateNull: 36,
    GetStaticMethodAsDelegate: 37,
    GetInstanceMethodAsDelegate: 38,
    PassDelegate: 39,
    InvokeDelegate: 40,
    ConvertType: 41,
    AddEventListener: 42,
    PluginWrapper: 43,
    GetAsyncOperationResult: 44
  }
);
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  CommandType
});
