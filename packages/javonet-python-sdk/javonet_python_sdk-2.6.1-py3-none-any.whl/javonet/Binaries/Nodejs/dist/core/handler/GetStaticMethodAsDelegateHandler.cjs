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
var GetStaticMethodAsDelegateHandler_exports = {};
__export(GetStaticMethodAsDelegateHandler_exports, {
  GetStaticMethodAsDelegateHandler: () => GetStaticMethodAsDelegateHandler
});
module.exports = __toCommonJS(GetStaticMethodAsDelegateHandler_exports);
var import_AbstractHandler = require("./AbstractHandler.cjs");
class GetStaticMethodAsDelegateHandler extends import_AbstractHandler.AbstractHandler {
  /** @type {Array<*>} */
  args = [];
  constructor() {
    super();
    this.method = null;
    this.requiredParametersCount = 2;
  }
  /**
   * Processes a command to retrieve a static method as a delegate.
   * @param {Command} command - The command containing payload data.
   * @returns {Function} The delegate for the static method.
   * @throws {Error} If the parameters mismatch or the method cannot be found.
   */
  process(command) {
    if (command.payload.length < this.requiredParametersCount) {
      throw new Error(`${this.constructor.name} parameters mismatch`);
    }
    const type = command.payload[0];
    const methodName = command.payload[1];
    this.args = command.payload.length > 2 ? command.payload.slice(2) : [];
    this.method = this.getMethod(type, methodName);
    if (!this.method) {
      throw this.createMethodNotFoundError(type, methodName);
    }
    const methodDelegate = this.method.bind(this);
    return methodDelegate;
  }
  /**
   * Retrieves the method from the type.
   * @param {Object} type - The class or constructor to search for the method.
   * @param {string} methodName - The name of the method.
   * @returns {Function|null} The found method or null if not found.
   */
  getMethod(type, methodName) {
    const method = (
      /** @type {any} */
      type[methodName]
    );
    return typeof method === "function" ? method : null;
  }
  /**
   * Creates an error message when the method is not found.
   * @param {Object} type - The class or constructor.
   * @param {string} methodName - The method name.
   * @returns {Error} The error with detailed message.
   */
  createMethodNotFoundError(type, methodName) {
    const methods = Object.keys(type).filter((key) => typeof /** @type {any} */
    type[key] === "function");
    const availableMethods = methods.map((name) => `${name}()`);
    const message = `Method ${methodName} not found in class ${/** @type {{name: string}} */
    type.name}. Available public static methods:
${availableMethods.join("\n")}`;
    return new Error(message);
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  GetStaticMethodAsDelegateHandler
});
