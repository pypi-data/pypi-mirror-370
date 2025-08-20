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
var PassDelegateHandler_exports = {};
__export(PassDelegateHandler_exports, {
  PassDelegateHandler: () => PassDelegateHandler
});
module.exports = __toCommonJS(PassDelegateHandler_exports);
var import_CommandType = require("../../utils/CommandType.cjs");
var import_InMemoryConnectionData = require("../../utils/connectionData/InMemoryConnectionData.cjs");
var import_DelegatesCache = require("../delegatesCache/DelegatesCache.cjs");
var import_AbstractHandler = require("./AbstractHandler.cjs");
class PassDelegateHandler extends import_AbstractHandler.AbstractHandler {
  /** @type {Interpreter | null | undefined} */
  interpreter = null;
  constructor(interpreter = null) {
    super();
    this.requiredParametersCount = 1;
    this.interpreter = interpreter;
  }
  /**S
   * Processes the given command to create and compile a delegate.
   * @param {Command} command - The command to process.
   * @returns {Function} The compiled delegate function.
   */
  process(command) {
    this.validateCommand(command);
    const delegateGuid = command.payload[0];
    const delegate = import_DelegatesCache.delegatesCacheInstance.getDelegate(delegateGuid);
    return delegate;
  }
  /**
   * Validates the command to ensure it has enough parameters.
   * @param {Command} command - The command to validate.
   */
  validateCommand(command) {
    if (command.payload.length < this.requiredParametersCount) {
      throw new Error("PassDelegateHandler parameters mismatch");
    }
  }
  /**
   * Retrieves the arguments from the command payload.
   * @param {Command} command - The command containing the payload.
   * @returns {Array<any>} The extracted arguments.
   */
  getArguments(command) {
    return command.payload.length > 2 ? command.payload.slice(2) : [];
  }
  /**
   * Extracts argument types from the arguments array.
   * @param {Array<any>} args - The arguments array.
   * @returns {Array<any>} The argument types.
   */
  getArgumentTypes(args) {
    return args.slice(0, -1).map((arg) => arg.constructor);
  }
  /**
   * Retrieves the return type from the arguments array.
   * @param {Array<any>} args - The arguments array.
   * @returns {Function} The return type.
   */
  getReturnType(args) {
    return args[args.length - 1].constructor;
  }
  /**
   * Creates parameter expressions from argument types.
   * @param {Array<any>} argsTypes - The argument types.
   * @returns {Array<any>} The parameter expressions.
   */
  createParameters(argsTypes) {
    return argsTypes.map((type, index) => ({ name: `arg${index}`, type }));
  }
  /**
   * Creates an array of arguments for the delegate.
   * @param {string} delegateGuid - The delegate identifier.
   * @param {Array<any>} parameters - The parameter expressions.
   * @returns {Array<any>} The arguments array.
   */
  createArgsArray(delegateGuid, parameters) {
    return [delegateGuid, ...parameters.map((param) => param.name)];
  }
  /**
   * Creates a command expression.
   * @param {string} callingRuntimeName - The runtime name.
   * @param {Array<any>} payload - The arguments array.
   * @returns {Object} The command object.
   */
  createCommand(callingRuntimeName, payload) {
    return {
      runtimeName: callingRuntimeName,
      type: import_CommandType.CommandType.InvokeDelegate,
      payload
    };
  }
  /**
   * Creates a method call to execute the command.
   * @param {Command} command - The command object.
   * @returns {any} The response object.
   */
  createExecuteCall(command) {
    return this.interpreter?.execute(command, new import_InMemoryConnectionData.InMemoryConnectionData());
  }
  /**
   * Retrieves the response payload from the execution call.
   * @param {Object<string, any>} executeCall - Object containing the execution call.
   * @returns {Array<any>} The response payload.
   */
  getResponse(executeCall) {
    return executeCall?.payload;
  }
  /**
   * Converts the first element of the response to the return type.
   * @param {Array<any>} response - The response payload.
   * @param {Function} returnType - The return type.
   * @returns {*} The converted first element.
   */
  convertFirstElement(response, returnType) {
    return returnType(response[0]);
  }
  /**
   * Creates a block of expressions for the delegate.
   * @param {Function} returnType - The return type.
   * @param {*} convertedFirstElement - The converted first element.
   * @returns {Object} The block expression.
   */
  createBlock(returnType, convertedFirstElement) {
    return { returnType, body: convertedFirstElement };
  }
  /**
   * Creates a delegate type.
   * @param {Array<any>} parameters - The parameter expressions.
   * @param {Function} returnType - The return type.
   * @returns {Function} The delegate type.
   */
  createDelegateType(parameters, returnType) {
    return (...args) => {
      if (args.length !== parameters.length) {
        throw new Error("Invalid argument count.");
      }
      return returnType;
    };
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  PassDelegateHandler
});
