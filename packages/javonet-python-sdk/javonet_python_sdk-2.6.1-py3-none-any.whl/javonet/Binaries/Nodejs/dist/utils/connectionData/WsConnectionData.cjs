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
var WsConnectionData_exports = {};
__export(WsConnectionData_exports, {
  WsConnectionData: () => WsConnectionData
});
module.exports = __toCommonJS(WsConnectionData_exports);
var import_ConnectionType = require("../ConnectionType.cjs");
var import_IConnectionData = require("./IConnectionData.cjs");
class WsConnectionData extends import_IConnectionData.IConnectionData {
  /**
   * @param {string} hostname - The hostname of the connection.
   */
  constructor(hostname) {
    super();
    this._hostname = hostname;
    this._connectionType = import_ConnectionType.ConnectionType.WEB_SOCKET;
  }
  /** @type {ConnectionType} */
  get connectionType() {
    return this._connectionType;
  }
  /** @type {string} */
  get hostname() {
    return this._hostname;
  }
  /** @type {string} */
  set hostname(value) {
    this._hostname = value;
  }
  /**
   * Serializes the connection data.
   * @returns {number[]} An array of connection data values.
   */
  serializeConnectionData() {
    return [this.connectionType, 0, 0, 0, 0, 0, 0];
  }
  /**
   * @param {WsConnectionData} other
   * @returns {boolean}
   */
  equals(other) {
    return other instanceof WsConnectionData && this._hostname === other.hostname;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  WsConnectionData
});
