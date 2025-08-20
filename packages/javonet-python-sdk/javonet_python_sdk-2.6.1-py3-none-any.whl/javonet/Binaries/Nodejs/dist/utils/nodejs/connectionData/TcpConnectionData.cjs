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
var TcpConnectionData_exports = {};
__export(TcpConnectionData_exports, {
  TcpConnectionData: () => TcpConnectionData
});
module.exports = __toCommonJS(TcpConnectionData_exports);
var import_IConnectionData = require("../../connectionData/IConnectionData.cjs");
var import_ConnectionType = require("../../ConnectionType.cjs");
var import_Runtime = require("../../Runtime.cjs");
const import_meta = {};
const requireDynamic = (0, import_Runtime.getRequire)(import_meta.url);
class TcpConnectionData extends import_IConnectionData.IConnectionData {
  /** @type {string} */
  ipAddress = "";
  /** @type {number} */
  _port = 0;
  /** @type {string} */
  _hostname = "";
  /** @type {ConnectionType} */
  _connectionType = import_ConnectionType.ConnectionType.TCP;
  /**
   * @param {string} hostname
   * @param {number} port
   */
  constructor(hostname, port) {
    super();
    this._port = port;
    this._hostname = hostname;
    this._connectionType = import_ConnectionType.ConnectionType.TCP;
    if (hostname === "localhost") {
      this.ipAddress = "127.0.0.1";
    } else {
      this.ipAddress = this.resolveIpAddress(hostname);
    }
  }
  /**
   * @returns {ConnectionType}
   */
  get connectionType() {
    return this._connectionType;
  }
  get hostname() {
    return this._hostname;
  }
  /**
   * @param {TcpConnectionData} other
   * @returns {boolean}
   */
  equals(other) {
    if (other instanceof TcpConnectionData) {
      return this.ipAddress === other.ipAddress && this._port === other._port;
    }
    return false;
  }
  /**
   * @param {string} hostname
   * @returns {string}
   */
  resolveIpAddress(hostname) {
    try {
      if ((0, import_Runtime.isNodejsRuntime)()) {
        const ipPattern = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
        if (ipPattern.test(hostname)) {
          return hostname;
        } else {
          const dns = requireDynamic("dns");
          return dns.resolve4(hostname, (err, addresses) => {
            if (err) {
              console.error(err);
              return "";
            }
            return addresses[0];
          });
        }
      }
      return "";
    } catch (error) {
      const err = (
        /** @type {{code?: string}} */
        error
      );
      if (err.code === "MODULE_NOT_FOUND") {
        throw new Error("dns module not found. Please install it using npm install dns");
      }
      throw error;
    }
  }
  /**
   * Serializes the connection data.
   * @returns {number[]} An array of connection data values.
   */
  serializeConnectionData() {
    let result = [this.connectionType];
    result = result.concat(this.#getAddressBytes());
    result = result.concat(this.#getPortBytes());
    return result;
  }
  /**
   * @returns {number[]} An array of address bytes.
   */
  #getAddressBytes() {
    return this.ipAddress.split(".").map(Number);
  }
  /**
   * @returns {number[]} An array of port bytes.
   */
  #getPortBytes() {
    return [this._port & 255, this._port >> 8];
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  TcpConnectionData
});
