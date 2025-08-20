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
var TypeDeserializer_exports = {};
__export(TypeDeserializer_exports, {
  TypeDeserializer: () => TypeDeserializer
});
module.exports = __toCommonJS(TypeDeserializer_exports);
var import_Command = require("../../utils/Command.cjs");
var import_buffer = require("buffer");
var import_StringEncodingMode = require("../../utils/StringEncodingMode.cjs");
class TypeDeserializer {
  /**
   * @param {Int8Array} encodedCommand
   * @returns {Command}
   */
  static deserializeCommand(encodedCommand) {
    return new import_Command.Command(encodedCommand[0], encodedCommand[1], []);
  }
  /**
   * @param {number} stringEncodingMode
   * @param {Int8Array} encodedString
   */
  static deserializeString(stringEncodingMode, encodedString) {
    switch (stringEncodingMode) {
      case import_StringEncodingMode.StringEncodingMode.ASCII:
        return String.fromCharCode(...encodedString);
      case import_StringEncodingMode.StringEncodingMode.UTF8: {
        const decoder = new TextDecoder("UTF-8");
        return decoder.decode(new Uint8Array(encodedString));
      }
      case import_StringEncodingMode.StringEncodingMode.UTF16: {
        let str = "";
        let newBuffer = new Uint8Array(encodedString);
        for (let i = 0; i < newBuffer.length; i++) {
          newBuffer[i] = encodedString[i];
        }
        for (let i = 0; i < encodedString.length; i = i + 2) {
          str += String.fromCharCode(newBuffer[i] + 256 * newBuffer[i + 1]);
        }
        return str;
      }
      case import_StringEncodingMode.StringEncodingMode.UTF32:
        throw "Type utf32-encoded string not supported in JavaScript";
      default:
        throw "Unknown string encoding - not supported in JavaScript";
    }
  }
  /**
   * @param {Int8Array} encodedInt
   */
  static deserializeInt(encodedInt) {
    return encodedInt[0] & 255 | (encodedInt[1] & 255) << 8 | (encodedInt[2] & 255) << 16 | (encodedInt[3] & 255) << 24;
  }
  /**
   * @param {Int8Array} encodedBool
   */
  static deserializeBool(encodedBool) {
    return encodedBool[0] === 1;
  }
  /**
   * @param {Int8Array} encodedFloat
   */
  static deserializeFloat(encodedFloat) {
    return import_buffer.Buffer.from(encodedFloat).readFloatLE();
  }
  /**
   * @param {Int8Array} encodedByte
   */
  static deserializeByte(encodedByte) {
    return import_buffer.Buffer.from(encodedByte).readUint8();
  }
  /**
   * @param {Int8Array} encodedChar
   */
  static deserializeChar(encodedChar) {
    return import_buffer.Buffer.from(encodedChar).readUint8();
  }
  /**
   * @param {Int8Array} encodedLongLong
   */
  static deserializeLongLong(encodedLongLong) {
    return import_buffer.Buffer.from(encodedLongLong).readBigInt64LE();
  }
  /**
   * @param {Int8Array} encodedDouble
   */
  static deserializeDouble(encodedDouble) {
    return import_buffer.Buffer.from(encodedDouble).readDoubleLE();
  }
  /**
   * @param {Int8Array} encodedULLong
   */
  static deserializeULLong(encodedULLong) {
    return import_buffer.Buffer.from(encodedULLong).readBigUInt64LE();
  }
  /**
   * @param {Int8Array} encodedUInt
   */
  static deserializeUInt(encodedUInt) {
    return import_buffer.Buffer.from(encodedUInt).readUIntLE(0, 4);
  }
  // eslint-disable-next-line no-unused-vars
  static deserializeNull(encodedNull = null) {
    return null;
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  TypeDeserializer
});
