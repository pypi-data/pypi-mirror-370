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
var RuntimeContext_exports = {};
__export(RuntimeContext_exports, {
  RuntimeContext: () => RuntimeContext
});
module.exports = __toCommonJS(RuntimeContext_exports);
var import_Command = require("../utils/Command.cjs");
var import_CommandType = require("../utils/CommandType.cjs");
var import_InvocationContext = require("./InvocationContext.cjs");
var import_ConnectionType = require("../utils/ConnectionType.cjs");
var import_ExceptionThrower = require("../utils/exception/ExceptionThrower.cjs");
var import_RuntimeName = require("../utils/RuntimeName.cjs");
var import_Interpreter = require("../core/interpreter/Interpreter.cjs");
var import_DelegatesCache = require("../core/delegatesCache/DelegatesCache.cjs");
var import_TypesHandler = require("../utils/TypesHandler.cjs");
var import_UtilsConst = require("../utils/UtilsConst.cjs");
var import_Runtime = require("../utils/Runtime.cjs");
const import_meta = {};
let _Transmitter = null;
const requireDynamic = (0, import_Runtime.getRequire)(import_meta.url);
class RuntimeContext {
  /** @type {Map<string, RuntimeContext>} */
  static memoryRuntimeContexts = /* @__PURE__ */ new Map();
  /** @type {Map<string, RuntimeContext>} */
  static networkRuntimeContexts = /* @__PURE__ */ new Map();
  /** @type {Map<string, RuntimeContext>} */
  static webSocketRuntimeContexts = /* @__PURE__ */ new Map();
  /** @type {Command | null} */
  #currentCommand = null;
  /** @type {Command | null} */
  #responseCommand = null;
  /** @type {Interpreter | null} */
  #interpreter = null;
  /**
   * @param {RuntimeNameType} runtimeName
   * @param {IConnectionData} connectionData
   */
  constructor(runtimeName, connectionData) {
    this._isExecuted = false;
    this.runtimeName = runtimeName;
    this.connectionData = connectionData;
    this.#interpreter = new import_Interpreter.Interpreter();
    if (this.connectionData.connectionType === import_ConnectionType.ConnectionType.WEB_SOCKET) {
      return;
    }
    if (this.runtimeName === import_RuntimeName.RuntimeName.Nodejs && this.connectionData.connectionType === import_ConnectionType.ConnectionType.IN_MEMORY) {
      return;
    }
    _Transmitter?.setJavonetWorkingDirectory(import_UtilsConst.UtilsConst.getJavonetWorkingDirectory());
    if (import_UtilsConst.UtilsConst.getConfigSource() !== "") {
      _Transmitter?.setConfigSource(import_UtilsConst.UtilsConst.getConfigSource());
    }
    _Transmitter?.activate(import_UtilsConst.UtilsConst.getLicenseKey());
  }
  /**
   * @param {RuntimeNameType} runtimeName
   * @param {IConnectionData} connectionData
   * @returns {RuntimeContext}
   */
  static getInstance(runtimeName, connectionData) {
    switch (connectionData.connectionType) {
      case import_ConnectionType.ConnectionType.IN_MEMORY:
        const key = String(runtimeName);
        if (RuntimeContext.memoryRuntimeContexts.has(key)) {
          const runtimeCtx = RuntimeContext.memoryRuntimeContexts.get(key);
          if (!runtimeCtx) throw new Error("Runtime context not found");
          runtimeCtx.#currentCommand = null;
          return runtimeCtx;
        } else {
          if (!_Transmitter) {
            const { Transmitter } = require("../core/transmitter/Transmitter.cjs");
            _Transmitter = Transmitter;
          }
          const runtimeCtx = new RuntimeContext(runtimeName, connectionData);
          RuntimeContext.memoryRuntimeContexts.set(key, runtimeCtx);
          return runtimeCtx;
        }
      case import_ConnectionType.ConnectionType.TCP: {
        const key1 = String(runtimeName) + JSON.stringify(connectionData);
        if (RuntimeContext.networkRuntimeContexts.has(key1)) {
          const runtimeCtx = RuntimeContext.networkRuntimeContexts.get(key1);
          if (!runtimeCtx) throw new Error("Runtime context not found");
          runtimeCtx.#currentCommand = null;
          return runtimeCtx;
        } else {
          if (!_Transmitter) {
            const { Transmitter } = require("../core/transmitter/Transmitter.cjs");
            _Transmitter = Transmitter;
          }
          const runtimeCtx = new RuntimeContext(runtimeName, connectionData);
          RuntimeContext.networkRuntimeContexts.set(key1, runtimeCtx);
          return runtimeCtx;
        }
      }
      case import_ConnectionType.ConnectionType.WEB_SOCKET: {
        const key2 = String(runtimeName) + JSON.stringify(connectionData);
        if (RuntimeContext.webSocketRuntimeContexts.has(key2)) {
          const runtimeCtx = RuntimeContext.webSocketRuntimeContexts.get(key2);
          if (!runtimeCtx) throw new Error("Runtime context not found");
          runtimeCtx.#currentCommand = null;
          return runtimeCtx;
        } else {
          const runtimeCtx = new RuntimeContext(runtimeName, connectionData);
          RuntimeContext.webSocketRuntimeContexts.set(key2, runtimeCtx);
          return runtimeCtx;
        }
      }
      default:
        throw new Error("Invalid connection type");
    }
  }
  /**
   * Executes the current command. The initial state of RuntimeContext is non-materialized,
   * wrapping either a single command or a chain of recursively nested commands.
   * Commands become nested through each invocation of methods on RuntimeContext.
   * Each invocation triggers the creation of a new RuntimeContext instance wrapping the current command with a new parent command.
   * The developer can decide at any moment of the materialization for the context, taking full control of the chunks of the expression being transferred and processed on the target runtime.
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/execute-method)
   * @method
   */
  execute() {
    this.#responseCommand = this.#interpreter?.execute(this.#currentCommand, this.connectionData);
    this.#currentCommand = null;
    if (this.#responseCommand === void 0) {
      throw new Error("responseCommand is undefined in Runtime Context execute method");
    }
    if (this.#responseCommand?.commandType === import_CommandType.CommandType.Exception) {
      throw import_ExceptionThrower.ExceptionThrower.throwException(this.#responseCommand);
    }
  }
  /**
   * Adds a reference to a library. Javonet allows you to reference and use modules or packages written in various languages.
   * This method allows you to use any library from all supported technologies. The necessary libraries need to be referenced.
   * The argument is a relative or full path to the library. If the library has dependencies on other libraries, the latter needs to be added first.
   * After referencing the library, any objects stored in this package can be used. Use static classes, create instances, call methods, use fields and properties, and much more.
   * @param {string} libraryPath - The relative or full path to the library.
   * @returns {RuntimeContext} RuntimeContext instance.
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/getting-started/adding-references-to-libraries)
   * @method
   */
  loadLibrary(libraryPath) {
    let localCommand = new import_Command.Command(this.runtimeName, import_CommandType.CommandType.LoadLibrary, [libraryPath]);
    this.#currentCommand = this.#buildCommand(localCommand);
    this.execute();
    return this;
  }
  /**
   * Retrieves a reference to a specific type. The type can be a class, interface or enum. The type can be retrieved from any referenced library.
   * @param {string} typeName - The full name of the type.
   * @param {...any} args - The arguments to be passed, if needed
   * @returns {InvocationContext} InvocationContext instance, that wraps the command to get the type.
   * @method
   */
  getType(typeName, ...args) {
    let localCommand = new import_Command.Command(this.runtimeName, import_CommandType.CommandType.GetType, [typeName, ...args]);
    this.#currentCommand = null;
    if (this.connectionData.connectionType === import_ConnectionType.ConnectionType.WEB_SOCKET) {
      return new import_InvocationContext.InvocationWsContext(
        this.runtimeName,
        this.connectionData,
        this.#buildCommand(localCommand)
      );
    }
    return new import_InvocationContext.InvocationContext(this.runtimeName, this.connectionData, this.#buildCommand(localCommand));
  }
  /**
   * Casts the provided value to a specific type. This method is used when invoking methods that require specific types of arguments.
   * The arguments include the target type and the value to be cast. The target type must be retrieved from the called runtime using the getType method.
   * After casting the value, it can be used as an argument when invoking methods.
   * @param {...any} args - The target type and the value to be cast.
   * @returns {InvocationContext} InvocationContext instance that wraps the command to cast the value.
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/casting/casting)
   * @method
   */
  cast(...args) {
    let localCommand = new import_Command.Command(this.runtimeName, import_CommandType.CommandType.Cast, args);
    this.#currentCommand = null;
    if (this.connectionData.connectionType === import_ConnectionType.ConnectionType.WEB_SOCKET) {
      return new import_InvocationContext.InvocationWsContext(
        this.runtimeName,
        this.connectionData,
        this.#buildCommand(localCommand)
      );
    }
    return new import_InvocationContext.InvocationContext(this.runtimeName, this.connectionData, this.#buildCommand(localCommand));
  }
  /**
   * Retrieves a specific item from an enum type. This method is used when working with enums from the called runtime.
   * The arguments include the enum type and the name of the item. The enum type must be retrieved from the called runtime using the getType method.
   * After retrieving the item, it can be used as an argument when invoking methods or for other operations.
   * @param {...any} args - The enum type and the name of the item.
   * @returns {InvocationContext} InvocationContext instance that wraps the command to get the enum item.
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/enums/using-enum-type)
   * @method
   */
  getEnumItem(...args) {
    let localCommand = new import_Command.Command(this.runtimeName, import_CommandType.CommandType.GetEnumItem, args);
    this.#currentCommand = null;
    if (this.connectionData.connectionType === import_ConnectionType.ConnectionType.WEB_SOCKET) {
      return new import_InvocationContext.InvocationWsContext(
        this.runtimeName,
        this.connectionData,
        this.#buildCommand(localCommand)
      );
    }
    return new import_InvocationContext.InvocationContext(this.runtimeName, this.connectionData, this.#buildCommand(localCommand));
  }
  /**
   * Creates a reference type argument that can be passed to a method with a ref parameter modifier. This method is used when working with methods from the called runtime that require arguments to be passed by reference.
   * The arguments include the value and optionally the type of the reference. The type must be retrieved from the called runtime using the getType method.
   * After creating the reference, it can be used as an argument when invoking methods.
   * @param {...any} args - The value and optionally the type of the reference.
   * @returns {InvocationContext} InvocationContext instance that wraps the command to create a reference as ref.
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/methods-arguments/passing-arguments-by-reference-with-ref-keyword)
   * @method
   */
  asRef(...args) {
    let localCommand = new import_Command.Command(this.runtimeName, import_CommandType.CommandType.AsRef, args);
    this.#currentCommand = null;
    if (this.connectionData.connectionType === import_ConnectionType.ConnectionType.WEB_SOCKET) {
      return new import_InvocationContext.InvocationWsContext(
        this.runtimeName,
        this.connectionData,
        this.#buildCommand(localCommand)
      );
    }
    return new import_InvocationContext.InvocationContext(this.runtimeName, this.connectionData, this.#buildCommand(localCommand));
  }
  /**
   * Creates a reference type argument that can be passed to a method with an out parameter modifier. This method is used when working with methods from the called runtime that require arguments to be passed by reference.
   * The arguments include the value and optionally the type of the reference. The type must be retrieved from the called runtime using the getType method.
   * After creating the reference, it can be used as an argument when invoking methods.
   * @param {...any} args - The value and optionally the type of the reference.
   * @returns {InvocationContext} InvocationContext instance that wraps the command to create a reference as out.
   * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/methods-arguments/passing-arguments-by-reference-with-out-keyword |Passing Arguments by Reference with out Keyword Guide)
   * @method
   */
  asOut(...args) {
    let localCommand = new import_Command.Command(this.runtimeName, import_CommandType.CommandType.AsOut, args);
    this.#currentCommand = null;
    if (this.connectionData.connectionType === import_ConnectionType.ConnectionType.WEB_SOCKET) {
      return new import_InvocationContext.InvocationWsContext(
        this.runtimeName,
        this.connectionData,
        this.#buildCommand(localCommand)
      );
    }
    return new import_InvocationContext.InvocationContext(this.runtimeName, this.connectionData, this.#buildCommand(localCommand));
  }
  /**
   * Invokes a function from the called runtime. This method is used when working with functions from the called runtime.
   * The arguments include the function name and the arguments to be passed to the function.
   * After invoking the function, the result can be used for further operations.
   * @param {string} functionName - The name of the function to invoke.
   * @param {...any} args - The arguments to be passed to the function.
   * @returns {InvocationContext} InvocationContext instance that wraps the command to invoke the function.
   * @see [Invoking Functions Guide](https://www.javonet.com/guides/v2/csharp/functions/invoking-functions)
   * @method
   */
  invokeGlobalFunction(functionName, ...args) {
    let localCommand = new import_Command.Command(this.runtimeName, import_CommandType.CommandType.InvokeGlobalFunction, [
      functionName,
      ...args
    ]);
    this.#currentCommand = null;
    if (this.connectionData.connectionType === import_ConnectionType.ConnectionType.WEB_SOCKET) {
      return new import_InvocationContext.InvocationWsContext(
        this.runtimeName,
        this.connectionData,
        this.#buildCommand(localCommand)
      );
    }
    return new import_InvocationContext.InvocationContext(this.runtimeName, this.connectionData, this.#buildCommand(localCommand));
  }
  /**
   * @param {Command} command
   * @returns {Command}
   */
  #buildCommand(command) {
    for (let i = 0; i < command.payload.length; i++) {
      command.payload[i] = this.#encapsulatePayloadItem(command.payload[i]);
    }
    return command.prependArgToPayload(this.#currentCommand);
  }
  /**
   * @param {unknown} payloadItem
   * @returns {Command}
   */
  #encapsulatePayloadItem(payloadItem) {
    if (payloadItem instanceof import_Command.Command) {
      for (let i = 0; i < payloadItem.payload.length; i++) {
        payloadItem.payload[i] = this.#encapsulatePayloadItem(payloadItem.payload[i]);
      }
      return payloadItem;
    } else if (payloadItem instanceof import_InvocationContext.InvocationContext) {
      const command = payloadItem?.get_current_command();
      if (!command) {
        throw new Error("Command not found");
      }
      return command;
    } else if (payloadItem instanceof Array) {
      const copiedArray = payloadItem.map((item) => this.#encapsulatePayloadItem(item));
      return new import_Command.Command(this.runtimeName, import_CommandType.CommandType.Array, copiedArray);
    } else if (typeof payloadItem === "function") {
      let newArray = new Array(payloadItem.length + 1);
      for (let i = 0; i < newArray.length; i++) {
        newArray[i] = "object";
      }
      const args = [import_DelegatesCache.delegatesCacheInstance.addDelegate(payloadItem), import_RuntimeName.RuntimeName.Nodejs].push(
        ...newArray
      );
      return new import_Command.Command(this.runtimeName, import_CommandType.CommandType.PassDelegate, args);
    } else if (import_TypesHandler.TypesHandler.isPrimitiveOrNullOrUndefined(payloadItem)) {
      return new import_Command.Command(this.runtimeName, import_CommandType.CommandType.Value, [payloadItem]);
    } else {
      throw Error(
        "Unsupported payload item type: " + (payloadItem?.constructor?.name || typeof payloadItem) + " for payload item: " + payloadItem
      );
    }
  }
  healthCheck() {
    let localCommand = new import_Command.Command(this.runtimeName, import_CommandType.CommandType.Value, ["health_check"]);
    this.#currentCommand = this.#buildCommand(localCommand);
    this.execute();
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  RuntimeContext
});
