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
var ExceptionSerializer_exports = {};
__export(ExceptionSerializer_exports, {
  ExceptionSerializer: () => ExceptionSerializer
});
module.exports = __toCommonJS(ExceptionSerializer_exports);
var import_CommandType = require("../CommandType.cjs");
var import_Command = require("../Command.cjs");
var import_RuntimeName = require("../RuntimeName.cjs");
var import_ExceptionType = require("../ExceptionType.cjs");
class ExceptionSerializer {
  static serializeException(exception, command) {
    let exceptionCommand = new import_Command.Command(import_RuntimeName.RuntimeName.Nodejs, import_CommandType.CommandType.Exception, []);
    let stackClasses = [];
    let stackMethods = [];
    let stackLines = [];
    let stackFiles = [];
    try {
      this.serializeStackTrace(exception, stackClasses, stackMethods, stackLines, stackFiles);
      exceptionCommand = exceptionCommand.addArgToPayload(this.getExceptionCode(exception));
      exceptionCommand = exceptionCommand.addArgToPayload(command ? command.toString() : "Command is null");
      exceptionCommand = exceptionCommand.addArgToPayload(exception.name);
      exceptionCommand = exceptionCommand.addArgToPayload(exception.message);
      exceptionCommand = exceptionCommand.addArgToPayload(stackClasses.join("|"));
      exceptionCommand = exceptionCommand.addArgToPayload(stackMethods.join("|"));
      exceptionCommand = exceptionCommand.addArgToPayload(stackLines.join("|"));
      exceptionCommand = exceptionCommand.addArgToPayload(stackFiles.join("|"));
    } catch (e) {
      exceptionCommand = new import_Command.Command(import_RuntimeName.RuntimeName.Nodejs, import_CommandType.CommandType.Exception, []);
      exceptionCommand = exceptionCommand.addArgToPayload(this.getExceptionCode(e));
      exceptionCommand = exceptionCommand.addArgToPayload(command ? command.toString() : "Command is null");
      exceptionCommand = exceptionCommand.addArgToPayload("Node.js Exception Serialization Error");
      exceptionCommand = exceptionCommand.addArgToPayload(e.message);
      exceptionCommand = exceptionCommand.addArgToPayload("ExceptionSerializer");
      exceptionCommand = exceptionCommand.addArgToPayload("serializeException");
      exceptionCommand = exceptionCommand.addArgToPayload("unknown");
      exceptionCommand = exceptionCommand.addArgToPayload("ExceptionSerializer.js");
    }
    return exceptionCommand;
  }
  static getExceptionCode(exception) {
    switch (exception.name) {
      case "Error":
        return import_ExceptionType.ExceptionType.EXCEPTION;
      case "TypeError":
        return import_ExceptionType.ExceptionType.ILLEGAL_ARGUMENT_EXCEPTION;
      case "RangeError":
        return import_ExceptionType.ExceptionType.INDEX_OUT_OF_BOUNDS_EXCEPTION;
      default:
        return import_ExceptionType.ExceptionType.EXCEPTION;
    }
  }
  static serializeStackTrace(exception, stackClasses, stackMethods, stackLines, stackFiles) {
    if (!exception || typeof exception.stack !== "string") {
      return;
    }
    const stackTrace = exception.stack.split("\n").slice(1);
    for (const line of stackTrace) {
      const trimmedLine = line.trim();
      if (trimmedLine.includes("Javonet.Node.js")) {
        continue;
      }
      let parts = trimmedLine.match(/at\s+(.*?)\s+\((.*?):(\d+):\d+\)/);
      if (parts) {
        const classAndMethod = parts[1].split(".");
        if (classAndMethod.length > 1) {
          stackClasses.push(classAndMethod[0]);
          stackMethods.push(classAndMethod.slice(1).join("."));
        } else {
          stackClasses.push("unknown");
          stackMethods.push(parts[1]);
        }
        stackFiles.push(parts[2]);
        stackLines.push(parts[3]);
        continue;
      }
      parts = trimmedLine.match(/at\s+(.*?):(\d+):\d+/);
      if (parts) {
        stackClasses.push("unknown");
        stackMethods.push("unknown");
        stackFiles.push(parts[1]);
        stackLines.push(parts[2]);
      }
    }
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  ExceptionSerializer
});
