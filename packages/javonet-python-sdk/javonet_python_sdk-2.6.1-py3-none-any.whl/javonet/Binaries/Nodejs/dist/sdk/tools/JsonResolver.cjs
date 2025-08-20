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
var JsonResolver_exports = {};
__export(JsonResolver_exports, {
  JsonResolver: () => JsonResolver
});
module.exports = __toCommonJS(JsonResolver_exports);
var import_Runtime = require("../../utils/Runtime.cjs");
const import_meta = {};
function isValidObject(param) {
  return typeof param === "object" && param !== null && !Array.isArray(param);
}
function isValidJson(param) {
  try {
    if (typeof param === "string") {
      const parsed = JSON.parse(param);
      return typeof parsed === "object" && parsed !== null;
    }
    return false;
  } catch (e) {
    return false;
  }
}
const requireDynamic = (0, import_Runtime.getRequire)(import_meta.url);
let fs = null;
class JsonResolver {
  /** @type {ConfigSource} */
  jsonObject;
  /** @type {string | ConfigSource} */
  configSource;
  /**
   * @param {string | ConfigSource} configSource
   */
  constructor(configSource) {
    this.configSource = JSON.stringify(configSource);
    this.jsonObject = this._getJsonObject(configSource);
  }
  /**
   * @returns {Partial<Runtimes>}
   */
  get runtimes() {
    return this.jsonObject?.runtimes || {};
  }
  /**
   * @returns {string}
   */
  get licenseKey() {
    return this.jsonObject?.licenseKey || "your-license-key";
  }
  /**
   * @returns {string}
   */
  get workingDirectory() {
    return this.jsonObject?.workingDirectory || "";
  }
  /**
   * @returns {string}
   */
  getLicenseKey() {
    if (!this.licenseKey) {
      throw new Error("License key not found in configuration source. Check your configuration source.");
    }
    return this.licenseKey;
  }
  /**
   * @returns {string}
   */
  getWorkingDirectory() {
    return this.workingDirectory;
  }
  /**
   * @param {RuntimeType} runtimeName
   * @param {string} configName
   * @returns {RuntimeChannelType}
   */
  getChannelType(runtimeName, configName) {
    const channel = this._getChannel(runtimeName, configName);
    return channel.type;
  }
  /**
   * @param {RuntimeType} runtimeName
   * @param {string} configName
   * @returns {string}
   */
  getChannelHost(runtimeName, configName) {
    const channel = this._getChannel(runtimeName, configName);
    if (channel.host === void 0) {
      throw new Error(`Host not found for channel in runtime ${runtimeName}, config ${configName}`);
    }
    return channel.host;
  }
  /**
   * @param {RuntimeType} runtimeName
   * @param {string} configName
   * @returns {number|string}
   */
  getChannelPort(runtimeName, configName) {
    const channel = this._getChannel(runtimeName, configName);
    if (channel.port === void 0) {
      throw new Error(`Port not found for channel in runtime ${runtimeName}, config ${configName}`);
    }
    return channel.port;
  }
  /**
   * @param {RuntimeType} runtimeName
   * @param {string} configName
   * @returns {string}
   */
  getModules(runtimeName, configName) {
    const runtime = this._getRuntime(runtimeName, configName);
    return runtime.modules || "";
  }
  /**
   * @private
   * @param {string | ConfigSource} configSource
   * @returns {ConfigSource}
   */
  _getJsonObject(configSource) {
    if (isValidObject(configSource)) {
      return (
        /** @type {ConfigSource} */
        configSource
      );
    }
    if (typeof configSource === "string" && isValidJson(configSource)) {
      const parsedJson = JSON.parse(configSource);
      if (isValidObject(parsedJson)) {
        return parsedJson;
      }
    }
    if ((0, import_Runtime.isNodejsRuntime)()) {
      if (!fs) {
        fs = requireDynamic("fs");
      }
      if (fs?.existsSync(configSource)) {
        const jsonText = fs.readFileSync(configSource, "utf8");
        if (isValidJson(jsonText)) {
          const parsedFromFile = JSON.parse(jsonText);
          if (isValidObject(parsedFromFile)) {
            return parsedFromFile;
          }
        }
      }
    }
    throw new Error(
      `Configuration source is not valid. Check your configuration:${String(this.configSource)}`
    );
  }
  /**
   * @private
   * @param {RuntimeType} runtimeName
   * @param {string} configName
   * @returns {Runtime}
   */
  _getRuntime(runtimeName, configName) {
    const runtimeList = this.runtimes[runtimeName];
    if (Array.isArray(runtimeList)) {
      const runtime = runtimeList.find((item) => item.name === configName);
      if (runtime) {
        return runtime;
      }
    } else if (typeof runtimeList?.name === "string" && runtimeList?.name === configName) {
      return runtimeList;
    }
    throw new Error(
      `Runtime config '${configName}' not found in configuration source for runtime '${runtimeName}'. Check your configuration source.`
    );
  }
  /**
   * @private
   * @param {RuntimeType} runtimeName
   * @param {string} configName
   * @returns {string}
   */
  _getRuntimeName(runtimeName, configName) {
    const runtime = this._getRuntime(runtimeName, configName);
    return runtime.name;
  }
  /**
   * @private
   * @param {RuntimeType} runtimeName
   * @param {string} configName
   * @returns {RuntimeChannel}
   */
  _getChannel(runtimeName, configName) {
    const runtime = this._getRuntime(runtimeName, configName);
    if (!runtime.channel) {
      throw new Error(
        `Channel not found for runtime config '${configName}' and runtime '${runtimeName}'. Check your configuration source.`
      );
    }
    return runtime.channel;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  JsonResolver
});
