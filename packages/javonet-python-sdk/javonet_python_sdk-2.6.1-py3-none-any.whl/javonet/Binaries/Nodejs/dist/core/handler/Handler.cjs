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
var Handler_exports = {};
__export(Handler_exports, {
  Handler: () => Handler,
  handlers: () => handlers
});
module.exports = __toCommonJS(Handler_exports);
var import_ReferencesCache = require("../referenceCache/ReferencesCache.cjs");
var import_ValueHandler = require("./ValueHandler.cjs");
var import_LoadLibraryHandler = require("./LoadLibraryHandler.cjs");
var import_GetTypeHandler = require("./GetTypeHandler.cjs");
var import_InvokeStaticMethodHandler = require("./InvokeStaticMethodHandler.cjs");
var import_GetStaticFieldHandler = require("./GetStaticFieldHandler.cjs");
var import_SetStaticFieldHandler = require("./SetStaticFieldHandler.cjs");
var import_ResolveReferenceHandler = require("./ResolveReferenceHandler.cjs");
var import_CreateClassInstanceHandler = require("./CreateClassInstanceHandler.cjs");
var import_GetInstanceFieldHandler = require("./GetInstanceFieldHandler.cjs");
var import_SetInstanceFieldHandler = require("./SetInstanceFieldHandler.cjs");
var import_InvokeInstanceMethodHandler = require("./InvokeInstanceMethodHandler.cjs");
var import_DestructReferenceHandler = require("./DestructReferenceHandler.cjs");
var import_CastingHandler = require("./CastingHandler.cjs");
var import_ArrayGetItemHandler = require("./ArrayGetItemHandler.cjs");
var import_ArrayGetSizeHandler = require("./ArrayGetSizeHandler.cjs");
var import_ArrayGetRankHandler = require("./ArrayGetRankHandler.cjs");
var import_ArraySetItemHandler = require("./ArraySetItemHandler.cjs");
var import_ArrayHandler = require("./ArrayHandler.cjs");
var import_EnableNamespaceHandler = require("./EnableNamespaceHandler.cjs");
var import_EnableTypeHandler = require("./EnableTypeHandler.cjs");
var import_GetStaticMethodAsDelegateHandler = require("./GetStaticMethodAsDelegateHandler.cjs");
var import_GetInstanceMethodAsDelegateHandler = require("./GetInstanceMethodAsDelegateHandler.cjs");
var import_PassDelegateHandler = require("./PassDelegateHandler.cjs");
var import_InvokeDelegateHandler = require("./InvokeDelegateHandler.cjs");
var import_InvokeGlobalFunctionHandler = require("./InvokeGlobalFunctionHandler.cjs");
var import_CommandType = require("../../utils/CommandType.cjs");
var import_Command = require("../../utils/Command.cjs");
var import_TypesHandler = require("../../utils/TypesHandler.cjs");
var import_ExceptionSerializer = require("../../utils/exception/ExceptionSerializer.cjs");
var import_ConvertTypeHandler = require("./ConvertTypeHandler.cjs");
var import_AbstractHandler = require("./AbstractHandler.cjs");
const handlers = {
  [import_CommandType.CommandType.Value]: new import_ValueHandler.ValueHandler(),
  [import_CommandType.CommandType.LoadLibrary]: new import_LoadLibraryHandler.LoadLibraryHandler(),
  [import_CommandType.CommandType.InvokeStaticMethod]: new import_InvokeStaticMethodHandler.InvokeStaticMethodHandler(),
  [import_CommandType.CommandType.GetType]: new import_GetTypeHandler.GetTypeHandler(),
  [import_CommandType.CommandType.GetStaticField]: new import_GetStaticFieldHandler.GetStaticFieldHandler(),
  [import_CommandType.CommandType.SetStaticField]: new import_SetStaticFieldHandler.SetStaticFieldHandler(),
  [import_CommandType.CommandType.CreateClassInstance]: new import_CreateClassInstanceHandler.CreateClassInstanceHandler(),
  [import_CommandType.CommandType.Reference]: new import_ResolveReferenceHandler.ResolveReferenceHandler(),
  [import_CommandType.CommandType.Cast]: new import_CastingHandler.CastingHandler(),
  [import_CommandType.CommandType.GetInstanceField]: new import_GetInstanceFieldHandler.GetInstanceFieldHandler(),
  [import_CommandType.CommandType.SetInstanceField]: new import_SetInstanceFieldHandler.SetInstanceFieldHandler(),
  [import_CommandType.CommandType.InvokeInstanceMethod]: new import_InvokeInstanceMethodHandler.InvokeInstanceMethodHandler(),
  [import_CommandType.CommandType.DestructReference]: new import_DestructReferenceHandler.DestructReferenceHandler(),
  [import_CommandType.CommandType.ArrayGetItem]: new import_ArrayGetItemHandler.ArrayGetItemHandler(),
  [import_CommandType.CommandType.ArrayGetSize]: new import_ArrayGetSizeHandler.ArrayGetSizeHandler(),
  [import_CommandType.CommandType.ArrayGetRank]: new import_ArrayGetRankHandler.ArrayGetRankHandler(),
  [import_CommandType.CommandType.ArraySetItem]: new import_ArraySetItemHandler.ArraySetItemHandler(),
  [import_CommandType.CommandType.Array]: new import_ArrayHandler.ArrayHandler(),
  [import_CommandType.CommandType.EnableNamespace]: new import_EnableNamespaceHandler.EnableNamespaceHandler(),
  [import_CommandType.CommandType.EnableType]: new import_EnableTypeHandler.EnableTypeHandler(),
  [import_CommandType.CommandType.GetStaticMethodAsDelegate]: new import_GetStaticMethodAsDelegateHandler.GetStaticMethodAsDelegateHandler(),
  [import_CommandType.CommandType.GetInstanceMethodAsDelegate]: new import_GetInstanceMethodAsDelegateHandler.GetInstanceMethodAsDelegateHandler(),
  [import_CommandType.CommandType.PassDelegate]: new import_PassDelegateHandler.PassDelegateHandler(),
  [import_CommandType.CommandType.InvokeDelegate]: new import_InvokeDelegateHandler.InvokeDelegateHandler(),
  [import_CommandType.CommandType.ConvertType]: new import_ConvertTypeHandler.ConvertTypeHandler(),
  [import_CommandType.CommandType.InvokeGlobalFunction]: new import_InvokeGlobalFunctionHandler.InvokeGlobalFunctionHandler()
};
class Handler {
  /**
   * @param {import('../interpreter/Interpreter.js').Interpreter} interpreter
   */
  constructor(interpreter) {
    this.interpreter = interpreter;
    if (!this.interpreter) {
      throw new Error("interpreter is undefined in Handler constructor");
    }
    handlers[import_CommandType.CommandType.PassDelegate] = new import_PassDelegateHandler.PassDelegateHandler(this.interpreter);
    Object.keys(handlers).forEach((commandTypeHandler) => {
      handlers[commandTypeHandler].handlers = handlers;
    });
  }
  /**
   * @param {Command} command
   */
  handleCommand(command) {
    try {
      if (command.commandType === import_CommandType.CommandType.RetrieveArray) {
        let responseArray = handlers[import_CommandType.CommandType.Reference].handleCommand(command.payload[0]);
        return import_Command.Command.createArrayResponse(responseArray, command.runtimeName);
      }
      let response = handlers[command.commandType].handleCommand(command);
      return this.parseCommand(response, command.runtimeName);
    } catch (e) {
      return import_ExceptionSerializer.ExceptionSerializer.serializeException(e, command);
    }
  }
  /**
   * @param {any} response
   * @param {RuntimeName} runtimeName
   * @returns {Command}
   */
  parseCommand(response, runtimeName) {
    if (import_TypesHandler.TypesHandler.isPrimitiveOrNullOrUndefined(response)) {
      return import_Command.Command.createResponse(response, runtimeName);
    } else {
      let cache = import_ReferencesCache.ReferencesCache.getInstance();
      let uuid = cache.cacheReference(response);
      return import_Command.Command.createReference(uuid, runtimeName);
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  Handler,
  handlers
});
