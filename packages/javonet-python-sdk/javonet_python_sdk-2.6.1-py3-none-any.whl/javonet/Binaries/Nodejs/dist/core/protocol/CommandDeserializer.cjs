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
var CommandDeserializer_exports = {};
__export(CommandDeserializer_exports, {
  CommandDeserializer: () => CommandDeserializer
});
module.exports = __toCommonJS(CommandDeserializer_exports);
var import_Command = require("../../utils/Command.cjs");
var import_Type = require("../../utils/Type.cjs");
var import_TypeDeserializer = require("./TypeDeserializer.cjs");
class CommandDeserializer {
  /**
   * @param {Int8Array} buffer
   */
  constructor(buffer) {
    this.buffer = buffer;
    this.command = new import_Command.Command(buffer[0], buffer[10], []);
    this.position = 11;
  }
  /**
   * @returns {Command}
   */
  deserialize() {
    while (!this.isAtEnd()) {
      this.command = this.command.addArgToPayload(this.readObject(this.buffer[this.position]));
    }
    return this.command;
  }
  isAtEnd() {
    return this.position === this.buffer.length;
  }
  /**
   * @param {number} typeNum
   * @returns {any}
   */
  readObject(typeNum) {
    const entry = Object.entries(import_Type.Type).find((entry2) => entry2[1] === typeNum);
    if (!entry) throw new Error("Unknown type number: " + typeNum);
    const type = entry[0];
    switch (type) {
      case "JAVONET_COMMAND":
        return this.readCommand();
      case "JAVONET_STRING":
        return this.readString();
      case "JAVONET_INTEGER":
        return this.readInt();
      case "JAVONET_BOOLEAN":
        return this.readBool();
      case "JAVONET_FLOAT":
        return this.readFloat();
      case "JAVONET_BYTE":
        return this.readByte();
      case "JAVONET_CHAR":
        return this.readChar();
      case "JAVONET_LONG_LONG":
        return this.readLongLong();
      case "JAVONET_DOUBLE":
        return this.readDouble();
      case "JAVONET_UNSIGNED_LONG_LONG":
        return this.readUllong;
      case "JAVONET_UNSIGNED_INTEGER":
        return this.readUInt();
      case "JAVONET_NULL":
        return this.readNull();
      default:
        throw "Unknown type - not supported in JavaScript";
    }
  }
  readCommand() {
    const p = this.position;
    const numberOfElementsInPayload = import_TypeDeserializer.TypeDeserializer.deserializeInt(this.buffer.slice(p + 1, p + 5));
    const runtime = this.buffer[p + 5];
    const commandType = this.buffer[p + 6];
    this.position += 7;
    const payload = new Array(numberOfElementsInPayload);
    for (let i = 0; i < numberOfElementsInPayload; i++) {
      payload[i] = this.readObject(this.buffer[this.position]);
    }
    return new import_Command.Command(runtime, commandType, payload);
  }
  // old implementation
  // readCommand() {
  //     const p = this.position
  //     const numberOfElementsInPayload = TypeDeserializer.deserializeInt(this.buffer.slice(p + 1, p + 5))
  //     const runtime = this.buffer[p + 5]
  //     const type = this.buffer[p + 6]
  //     this.position += 7
  //     const command = new Command(runtime, type, [])
  //     return this.readCommandRecursively(numberOfElementsInPayload, command)
  // }
  //
  // readCommandRecursively(numberOfElementsInPayloadLeft, cmd) {
  //     if (numberOfElementsInPayloadLeft === 0) return cmd
  //     const p = this.position
  //     cmd = cmd.addArgToPayload(this.readObject(this.buffer[p]))
  //     return this.readCommandRecursively(numberOfElementsInPayloadLeft - 1, cmd)
  // }
  readString() {
    let p = this.position;
    const stringEncodingMode = this.buffer[p + 1];
    const size = import_TypeDeserializer.TypeDeserializer.deserializeInt(this.buffer.slice(p + 2, p + 6));
    this.position += 6;
    p = this.position;
    this.position += size;
    return import_TypeDeserializer.TypeDeserializer.deserializeString(stringEncodingMode, this.buffer.slice(p, p + size));
  }
  readInt() {
    const size = 4;
    this.position += 2;
    const p = this.position;
    this.position += size;
    return import_TypeDeserializer.TypeDeserializer.deserializeInt(this.buffer.slice(p, p + size));
  }
  readBool() {
    const size = 1;
    this.position += 2;
    const p = this.position;
    this.position += size;
    return import_TypeDeserializer.TypeDeserializer.deserializeBool(this.buffer.slice(p, p + size));
  }
  readFloat() {
    const size = 4;
    this.position += 2;
    const p = this.position;
    this.position += size;
    return import_TypeDeserializer.TypeDeserializer.deserializeFloat(this.buffer.slice(p, p + size));
  }
  readByte() {
    const size = 1;
    this.position += 2;
    const p = this.position;
    this.position += size;
    return import_TypeDeserializer.TypeDeserializer.deserializeByte(this.buffer.slice(p, p + size));
  }
  readChar() {
    const size = 1;
    this.position += 2;
    const p = this.position;
    this.position += size;
    return import_TypeDeserializer.TypeDeserializer.deserializeChar(this.buffer.slice(p, p + size));
  }
  readLongLong() {
    const size = 8;
    this.position += 2;
    const p = this.position;
    this.position += size;
    return import_TypeDeserializer.TypeDeserializer.deserializeLongLong(this.buffer.slice(p, p + size));
  }
  readDouble() {
    const size = 8;
    this.position += 2;
    const p = this.position;
    this.position += size;
    return import_TypeDeserializer.TypeDeserializer.deserializeDouble(this.buffer.slice(p, p + size));
  }
  readUllong() {
    const size = 8;
    this.position += 2;
    const p = this.position;
    this.position += size;
    return import_TypeDeserializer.TypeDeserializer.deserializeULLong(this.buffer.slice(p, p + size));
  }
  readUInt() {
    const size = 4;
    this.position += 2;
    const p = this.position;
    this.position += size;
    return import_TypeDeserializer.TypeDeserializer.deserializeUInt(this.buffer.slice(p, p + size));
  }
  readNull() {
    const size = 1;
    this.position += 2;
    this.position += size;
    return import_TypeDeserializer.TypeDeserializer.deserializeNull();
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  CommandDeserializer
});
