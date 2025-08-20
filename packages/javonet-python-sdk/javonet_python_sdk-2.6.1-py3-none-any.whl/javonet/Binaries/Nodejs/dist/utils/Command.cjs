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
var Command_exports = {};
__export(Command_exports, {
  Command: () => Command
});
module.exports = __toCommonJS(Command_exports);
var import_CommandType = require("./CommandType.cjs");
class Command {
  /**
   * Constructs a new Command instance.
   * @param {RuntimeName} runtimeName - The runtime name associated with the command.
   * @param {number} commandType - The type of the command.
   * @param {any} [payload] - The optional payload of the command.
   * @method
   */
  constructor(runtimeName, commandType, payload = []) {
    this.runtimeName = runtimeName;
    this.commandType = commandType;
    this.payload = payload;
  }
  /**
   * @param {unknown} response
   * @param {RuntimeName} runtimeName
   * @returns {Command}
   */
  static createResponse(response, runtimeName) {
    return new Command(runtimeName, import_CommandType.CommandType.Value, [response]);
  }
  /**
   * @param {unknown} response
   * @param {RuntimeName} runtimeName
   * @returns {Command}
   */
  static createReference(response, runtimeName) {
    return new Command(runtimeName, import_CommandType.CommandType.Reference, [response]);
  }
  /**
   * @param {unknown} response
   * @param {RuntimeName} runtimeName
   * @returns {Command}
   */
  static createArrayResponse(response, runtimeName) {
    return new Command(runtimeName, import_CommandType.CommandType.Array, response);
  }
  dropFirstPayloadArg() {
    return new Command(this.runtimeName, this.commandType, this.payload.slice(1));
  }
  /**
   * @param {any} arg
   * @returns {Command}
   */
  addArgToPayload(arg) {
    return new Command(this.runtimeName, this.commandType, this.payload.concat(arg));
  }
  /**
   * @param {Command|null} current_command
   * @returns {Command}
   */
  prependArgToPayload(current_command) {
    if (current_command == null) {
      return new Command(this.runtimeName, this.commandType, this.payload);
    } else {
      return new Command(this.runtimeName, this.commandType, [current_command].concat(this.payload));
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  Command
});
