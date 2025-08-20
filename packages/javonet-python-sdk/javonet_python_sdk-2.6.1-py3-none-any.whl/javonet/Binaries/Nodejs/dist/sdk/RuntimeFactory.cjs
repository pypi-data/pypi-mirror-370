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
var RuntimeFactory_exports = {};
__export(RuntimeFactory_exports, {
  RuntimeFactory: () => RuntimeFactory
});
module.exports = __toCommonJS(RuntimeFactory_exports);
var import_RuntimeName = require("../utils/RuntimeName.cjs");
var import_RuntimeContext = require("./RuntimeContext.cjs");
class RuntimeFactory {
  /**
   * @param {IConnectionData} connectionData 
   */
  constructor(connectionData) {
    this.connectionData = connectionData;
  }
  /**
   * Creates RuntimeContext instance to interact with the .NET Framework runtime.
   * @return {RuntimeContext} a RuntimeContext instance for the .NET Framework runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  clr() {
    return import_RuntimeContext.RuntimeContext.getInstance(import_RuntimeName.RuntimeName.Clr, this.connectionData);
  }
  /**
   * Creates RuntimeContext instance to interact with the JVM runtime.
   * @return {RuntimeContext} a RuntimeContext instance for the JVM runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  jvm() {
    return import_RuntimeContext.RuntimeContext.getInstance(import_RuntimeName.RuntimeName.Jvm, this.connectionData);
  }
  /**
   * Creates RuntimeContext instance to interact with the .NET runtime.
   * @return {RuntimeContext} a RuntimeContext instance for the .NET runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  netcore() {
    return import_RuntimeContext.RuntimeContext.getInstance(import_RuntimeName.RuntimeName.Netcore, this.connectionData);
  }
  /**
   * Creates RuntimeContext instance to interact with the Perl runtime.
   * @return {RuntimeContext} a RuntimeContext instance for the Perl runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  perl() {
    return import_RuntimeContext.RuntimeContext.getInstance(import_RuntimeName.RuntimeName.Perl, this.connectionData);
  }
  /**
   * Creates RuntimeContext instance to interact with the Python runtime.
   * @return {RuntimeContext} a RuntimeContext instance for the Python runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  python() {
    return import_RuntimeContext.RuntimeContext.getInstance(import_RuntimeName.RuntimeName.Python, this.connectionData);
  }
  /**
   * Creates RuntimeContext instance to interact with the Ruby runtime.
   * @return {RuntimeContext} a RuntimeContext instance for the Ruby runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  ruby() {
    return import_RuntimeContext.RuntimeContext.getInstance(import_RuntimeName.RuntimeName.Ruby, this.connectionData);
  }
  /**
   * Creates RuntimeContext instance to interact with Node.js runtime.
   * @return {RuntimeContext} a RuntimeContext instance for the Node.js runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  nodejs() {
    return import_RuntimeContext.RuntimeContext.getInstance(import_RuntimeName.RuntimeName.Nodejs, this.connectionData);
  }
  /**
   * Creates RuntimeContext instance to interact with the Python runtime.
   * @return {RuntimeContext} a RuntimeContext instance for the Python runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  python27() {
    return import_RuntimeContext.RuntimeContext.getInstance(import_RuntimeName.RuntimeName.Python27, this.connectionData);
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  RuntimeFactory
});
