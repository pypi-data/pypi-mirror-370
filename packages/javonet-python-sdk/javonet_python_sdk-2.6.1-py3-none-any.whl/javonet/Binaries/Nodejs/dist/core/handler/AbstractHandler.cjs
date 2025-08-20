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
var AbstractHandler_exports = {};
__export(AbstractHandler_exports, {
  AbstractHandler: () => AbstractHandler
});
module.exports = __toCommonJS(AbstractHandler_exports);
var import_Command = require("../../utils/Command.cjs");
class AbstractHandler {
  /**
   * @type {Record<number, AbstractHandler>}
   */
  handlers = [];
  constructor() {
    if (new.target === AbstractHandler) throw new TypeError("You cannot instantiate abstract class");
  }
  /**
   * @param {Command} command
   */
  process(command) {
    throw new Error("process must be implemented");
  }
  /**
   * @param {Command} command
   */
  handleCommand(command) {
    this.iterate(command);
    return this.process(command);
  }
  /**
   * @param {Command} command
   */
  iterate(command) {
    for (let i = 0; i < command.payload.length; i++) {
      if (command.payload[i] instanceof import_Command.Command) {
        let inner = command.payload[i];
        command.payload[i] = this.handlers[inner.commandType].handleCommand(inner);
      }
    }
  }
  /**
   * 
   * @param {*} error 
   * @param {*} class_name 
   * @returns 
   */
  process_stack_trace(error, class_name) {
    let stackTraceArray = error.stack.split("\n").map((frame) => frame.trim());
    stackTraceArray.forEach((str, index) => {
      if (str.includes(class_name)) {
        stackTraceArray = stackTraceArray.slice(0, index).filter((s) => !s.includes(class_name));
      }
    });
    error.stack = stackTraceArray.join(" \n ");
    return error;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  AbstractHandler
});
