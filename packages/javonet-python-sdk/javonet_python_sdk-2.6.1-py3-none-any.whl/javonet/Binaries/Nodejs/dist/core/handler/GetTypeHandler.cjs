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
var GetTypeHandler_exports = {};
__export(GetTypeHandler_exports, {
  GetTypeHandler: () => GetTypeHandler
});
module.exports = __toCommonJS(GetTypeHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
var import_LoadLibraryHandler = require("./LoadLibraryHandler.cjs");
var import_NamespaceCache = require("../namespaceCache/NamespaceCache.cjs");
var import_TypeCache = require("../typeCache/TypeCache.cjs");
var import_Runtime = require("../../utils/Runtime.cjs");
const import_meta = {};
class GetTypeHandler extends import_AbstractHandler.AbstractHandler {
  constructor() {
    super();
    this.requiredParametersCount = 1;
    this.namespaceCache = new import_NamespaceCache.NamespaceCache();
    this.typeCache = new import_TypeCache.TypeCache();
    this.loadLibaryHandler = new import_LoadLibraryHandler.LoadLibraryHandler();
  }
  /**
   * 
   * @param {Command} command 
   * @returns 
   */
  process(command) {
    try {
      if (command.payload.length < this.requiredParametersCount) {
        throw new Error("Get Type parameters mismatch");
      }
      const { payload } = command;
      let typeName = payload[0];
      typeName = typeName.replace(".js", "");
      const typeToReturn = (
        /** @type {any} */
        global[typeName]
      );
      if (typeToReturn === void 0) {
        let message = `Type ${typeName} not found
`;
        message += "Available types:\n";
        message += this.getAvailableTypes().join("\n");
        throw new Error(message);
      }
      if (this.namespaceCache.isNamespaceCacheEmpty() && this.typeCache.isTypeCacheEmpty() || // both caches are empty
      this.namespaceCache.isTypeAllowed(typeToReturn) || // namespace is allowed
      this.typeCache.isTypeAllowed(typeToReturn)) {
      } else {
        let allowed_namespaces = this.namespaceCache.getCachedNamespaces().join(", ");
        let allowed_types = this.typeCache.getCachedTypes().join(", ");
        throw new Error(
          `Type ${typeToReturn.name} not allowed. 
Allowed namespaces: ${allowed_namespaces}
Allowed types: ${allowed_types}`
        );
      }
      return typeToReturn;
    } catch (error) {
      throw this.process_stack_trace(error, this.constructor.name);
    }
  }
  getAvailableTypes() {
    const availableTypes = [];
    this.loadLibaryHandler.getLoadedLibraries().forEach((lib) => {
      const dynamicRequire = (0, import_Runtime.getRequire)(import_meta.url);
      const moduleExports = dynamicRequire(`${lib}`);
      availableTypes.push(moduleExports.name);
      Object.keys(moduleExports).forEach((key) => {
        availableTypes.push(key);
      });
    });
    return availableTypes;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  GetTypeHandler
});
