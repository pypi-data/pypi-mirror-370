export class TypeDeserializer {
    /**
     * @param {Int8Array} encodedCommand
     * @returns {Command}
     */
    static deserializeCommand(encodedCommand: Int8Array): Command;
    /**
     * @param {number} stringEncodingMode
     * @param {Int8Array} encodedString
     */
    static deserializeString(stringEncodingMode: number, encodedString: Int8Array): string;
    /**
     * @param {Int8Array} encodedInt
     */
    static deserializeInt(encodedInt: Int8Array): number;
    /**
     * @param {Int8Array} encodedBool
     */
    static deserializeBool(encodedBool: Int8Array): boolean;
    /**
     * @param {Int8Array} encodedFloat
     */
    static deserializeFloat(encodedFloat: Int8Array): number;
    /**
     * @param {Int8Array} encodedByte
     */
    static deserializeByte(encodedByte: Int8Array): number;
    /**
     * @param {Int8Array} encodedChar
     */
    static deserializeChar(encodedChar: Int8Array): number;
    /**
     * @param {Int8Array} encodedLongLong
     */
    static deserializeLongLong(encodedLongLong: Int8Array): bigint;
    /**
     * @param {Int8Array} encodedDouble
     */
    static deserializeDouble(encodedDouble: Int8Array): number;
    /**
     * @param {Int8Array} encodedULLong
     */
    static deserializeULLong(encodedULLong: Int8Array): bigint;
    /**
     * @param {Int8Array} encodedUInt
     */
    static deserializeUInt(encodedUInt: Int8Array): number;
    static deserializeNull(encodedNull?: null): null;
}
import { Command } from '../../utils/Command.js';
