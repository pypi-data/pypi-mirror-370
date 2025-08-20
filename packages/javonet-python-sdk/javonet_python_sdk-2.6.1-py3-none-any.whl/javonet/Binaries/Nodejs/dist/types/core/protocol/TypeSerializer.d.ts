export class TypeSerializer {
    /**
     * @param {unknown} payload_item
     */
    static serializePrimitive(payload_item: unknown): Buffer<ArrayBuffer>;
    /**
     * @param {Command} command
     */
    static serializeCommand(command: Command): Buffer<ArrayBuffer>;
    /**
     * @param {string} string_value
     */
    static serializeString(string_value: string): Buffer<ArrayBuffer>;
    /**
     * @param {number} int_value
     */
    static serializeInt(int_value: number): Buffer<ArrayBuffer>;
    /**
     * @param {boolean} bool_value
     */
    static serializeBool(bool_value: boolean): Buffer<ArrayBuffer>;
    /**
     * @param {number} float_value
     */
    static serializeFloat(float_value: number): Buffer<ArrayBuffer>;
    /**
     * @param {number} byte_value
     */
    static serializeByte(byte_value: number): Buffer<ArrayBuffer>;
    /**
     * @param {number} char_value
     */
    static serializeChar(char_value: number): Buffer<ArrayBuffer>;
    /**
     * @param {number} longlong_value
     */
    static serializeLongLong(longlong_value: number): Buffer<ArrayBuffer>;
    /**
     * @param {number} double_value
     */
    static serializeDouble(double_value: number): Buffer<ArrayBuffer>;
    /**
     * @param {bigint} ullong_value
     */
    static serializeULLong(ullong_value: bigint): Buffer<ArrayBuffer>;
    /**
     * @param {number} uint_value
     */
    static serializeUInt(uint_value: number): Buffer<ArrayBuffer>;
    static serializeNull(): Buffer<ArrayBuffer>;
    /**
     * @param {number} int_value
     */
    static serializeIntValue(int_value: number): Buffer<ArrayBuffer>;
}
import { Buffer } from 'buffer';
import { Command } from '../../utils/Command.js';
