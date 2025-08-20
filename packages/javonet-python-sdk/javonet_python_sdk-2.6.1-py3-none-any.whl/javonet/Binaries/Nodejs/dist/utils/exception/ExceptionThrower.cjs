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
var ExceptionThrower_exports = {};
__export(ExceptionThrower_exports, {
  ExceptionThrower: () => ExceptionThrower
});
module.exports = __toCommonJS(ExceptionThrower_exports);
var import_ExceptionType = require("../ExceptionType.cjs");
class ExceptionThrower {
  static throwException(commandException) {
    let exceptionType = import_ExceptionType.ExceptionType.EXCEPTION;
    let javonetStackCommand = "";
    let exceptionName = "Node.js exception";
    let exceptionMessage = "Node.js exception with empty message";
    let stackTraceClasses = "";
    let stackTraceMethods = "";
    let stackTraceLines = "";
    let stackTraceFiles = "";
    switch (commandException.payload.length) {
      case 8:
        stackTraceFiles = commandException.payload[7];
      case 7:
        stackTraceLines = commandException.payload[6];
      case 6:
        stackTraceMethods = commandException.payload[5];
      case 5:
        stackTraceClasses = commandException.payload[4];
      case 4:
        exceptionMessage = commandException.payload[3];
      case 3:
        exceptionName = commandException.payload[2];
      case 2:
        javonetStackCommand = commandException.payload[1];
      case 1:
        exceptionType = commandException.payload[0];
      default:
        break;
    }
    let error;
    switch (exceptionType) {
      case import_ExceptionType.ExceptionType.EXCEPTION:
      case import_ExceptionType.ExceptionType.IO_EXCEPTION:
      case import_ExceptionType.ExceptionType.FILE_NOT_FOUND_EXCEPTION:
      case import_ExceptionType.ExceptionType.RUNTIME_EXCEPTION:
      case import_ExceptionType.ExceptionType.ARITHMETIC_EXCEPTION:
        error = new Error();
        break;
      case import_ExceptionType.ExceptionType.ILLEGAL_ARGUMENT_EXCEPTION:
      case import_ExceptionType.ExceptionType.NULL_POINTER_EXCEPTION:
        error = new TypeError();
        break;
      case import_ExceptionType.ExceptionType.INDEX_OUT_OF_BOUNDS_EXCEPTION:
        error = new RangeError();
        break;
      default:
        error = new Error();
    }
    error.stack = this.serializeStack(
      stackTraceClasses,
      stackTraceMethods,
      stackTraceLines,
      stackTraceFiles
    );
    error.name = exceptionName;
    error.message = exceptionMessage;
    return error;
  }
  static serializeStack(stackTraceClasses, stackTraceMethods, stackTraceLines, stackTraceFiles) {
    let stackTraceClassesArray = stackTraceClasses.split("|");
    let stackTraceMethodsArray = stackTraceMethods.split("|");
    let stackTraceLinesArray = stackTraceLines.split("|");
    let stackTraceFilesArray = stackTraceFiles.split("|");
    let stackTrace = "";
    for (let i = 0; i < stackTraceClassesArray.length; i++) {
      if (stackTraceClassesArray[i] != "") {
        stackTrace += `    at ${stackTraceClassesArray[i]}`;
      }
      if (i < stackTraceMethodsArray.length && stackTraceMethodsArray[i] != "") {
        stackTrace += `.${stackTraceMethodsArray[i]}`;
      }
      if (i < stackTraceFilesArray.length && stackTraceFilesArray[i] != "") {
        stackTrace += ` ${stackTraceFilesArray[i]}`;
      }
      if (i < stackTraceLinesArray.length && stackTraceLinesArray[i] != "") {
        stackTrace += `:${stackTraceLinesArray[i]}`;
      }
      stackTrace += "\n";
    }
    return stackTrace;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ExceptionThrower
});
