export class CommandDeserializer {
    /**
     * @param {Int8Array} buffer
     */
    constructor(buffer: Int8Array);
    buffer: Int8Array<ArrayBufferLike>;
    command: Command;
    position: number;
    /**
     * @returns {Command}
     */
    deserialize(): Command;
    isAtEnd(): boolean;
    /**
     * @param {number} typeNum
     * @returns {any}
     */
    readObject(typeNum: number): any;
    readCommand(): Command;
    readString(): string;
    readInt(): number;
    readBool(): boolean;
    readFloat(): number;
    readByte(): number;
    readChar(): number;
    readLongLong(): bigint;
    readDouble(): number;
    readUllong(): bigint;
    readUInt(): number;
    readNull(): null;
}
import { Command } from '../../utils/Command.js';
