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
var ConfigRuntimeFactory_exports = {};
__export(ConfigRuntimeFactory_exports, {
  ConfigRuntimeFactory: () => ConfigRuntimeFactory
});
module.exports = __toCommonJS(ConfigRuntimeFactory_exports);
var import_WsConnectionData = require("../utils/connectionData/WsConnectionData.cjs");
var import_TcpConnectionData = require("../utils/nodejs/connectionData/TcpConnectionData.cjs");
var import_RuntimeName = require("../utils/RuntimeName.cjs");
var import_RuntimeNameHandler = require("../utils/RuntimeNameHandler.cjs");
var import_RuntimeContext = require("./RuntimeContext.cjs");
var import_Runtime = require("../utils/Runtime.cjs");
var import_InMemoryConnectionData = require("../utils/connectionData/InMemoryConnectionData.cjs");
var import_JsonResolver = require("./tools/JsonResolver.cjs");
var import_UtilsConst = require("../utils/UtilsConst.cjs");
const import_meta = {};
const requireDynamic = (0, import_Runtime.getRequire)(import_meta.url);
class ConfigRuntimeFactory {
  /**
   * @param {ConfigSource | string} configSource
   */
  constructor(configSource) {
    this.configSource = configSource;
  }
  /**
   * Creates RuntimeContext instance to interact with the .NET Framework runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the .NET Framework runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  clr(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Clr, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with the JVM runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the JVM runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  jvm(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Jvm, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with the .NET runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the .NET runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  netcore(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Netcore, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with the Perl runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the Perl runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  perl(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Perl, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with the Python runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the Python runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  python(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Python, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with the Ruby runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the Ruby runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  ruby(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Ruby, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with Node.js runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the Node.js runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  nodejs(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Nodejs, configName);
  }
  /**
   * Creates RuntimeContext instance to interact with the Python 2.7 runtime.
   * @param {string} [configName="default"] - The name of the configuration to use (optional).
   * @return {RuntimeContext} a RuntimeContext instance for the Python 2.7 runtime
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
   */
  python27(configName = "default") {
    return this.#getRuntimeContext(import_RuntimeName.RuntimeName.Python27, configName);
  }
  /**
   * @param {RuntimeNameType} runtime
   * @param {string} configName
   * @returns {RuntimeContext}
   */
  #getRuntimeContext(runtime, configName = "default") {
    const jsonResolver = new import_JsonResolver.JsonResolver(this.configSource);
    import_UtilsConst.UtilsConst.setLicenseKey(jsonResolver.getLicenseKey());
    if (jsonResolver.getWorkingDirectory()) {
      import_UtilsConst.UtilsConst.setJavonetWorkingDirectory(jsonResolver.getWorkingDirectory());
    }
    if ((0, import_Runtime.isBrowserRuntime)()) {
      const channelType = jsonResolver.getChannelType(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName);
      let connectionData = null;
      if (channelType === "webSocket") {
        connectionData = new import_WsConnectionData.WsConnectionData(
          jsonResolver.getChannelHost(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName)
        );
      } else {
        throw new Error("Unsupported connection type: " + channelType);
      }
      const rtmCtx = import_RuntimeContext.RuntimeContext.getInstance(runtime, connectionData);
      this.#loadModules(runtime, configName, jsonResolver, rtmCtx);
      return rtmCtx;
    }
    if ((0, import_Runtime.isNodejsRuntime)()) {
      try {
        const channelType = jsonResolver.getChannelType(
          import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime),
          configName
        );
        const licenseKey = jsonResolver.getLicenseKey();
        let connectionData = null;
        if (channelType === "inMemory") {
          connectionData = new import_InMemoryConnectionData.InMemoryConnectionData();
        } else if (channelType === "tcp") {
          connectionData = new import_TcpConnectionData.TcpConnectionData(
            jsonResolver.getChannelHost(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName),
            /** @type {number} */
            jsonResolver.getChannelPort(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName)
          );
        } else if (channelType === "webSocket") {
          connectionData = new import_WsConnectionData.WsConnectionData(
            jsonResolver.getChannelHost(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName)
          );
        } else {
          throw new Error("Unsupported connection type: " + channelType);
        }
        const rtmCtx = import_RuntimeContext.RuntimeContext.getInstance(runtime, connectionData);
        this.#loadModules(runtime, configName, jsonResolver, rtmCtx);
        return rtmCtx;
      } catch (error) {
        throw error;
      }
    }
    throw new Error("Unsupported runtime environment");
  }
  /**
   * @param {number} runtime
   * @param {string} configName
   * @param {JsonResolver} jsonResolver
   * @param {RuntimeContext} rtmCtx
   */
  #loadModules(runtime, configName, jsonResolver, rtmCtx) {
    try {
      const modules = jsonResolver.getModules(import_RuntimeNameHandler.RuntimeNameHandler.getName(runtime), configName).split(",").filter((module2) => module2.trim() !== "");
      if ((0, import_Runtime.isNodejsRuntime)()) {
        const path = (
          /** @type {import('path').PlatformPath} */
          /** @type {unknown} */
          requireDynamic("path")
        );
        const configDirectoryAbsolutePath = process.cwd();
        modules.forEach((module2) => {
          if (path.isAbsolute(module2)) {
            rtmCtx.loadLibrary(module2);
          } else {
            rtmCtx.loadLibrary(path.join(configDirectoryAbsolutePath, module2));
          }
        });
      }
    } catch (error) {
      throw error;
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ConfigRuntimeFactory
});
