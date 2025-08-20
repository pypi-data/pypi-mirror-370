export class Receiver {
    static connectionData: InMemoryConnectionData;
    static getRuntimeInfo(): string;
    /**
     * @param {Int8Array} messageByteArray
     */
    static sendCommand(messageByteArray: Int8Array): Int8Array<ArrayBufferLike>;
    /**
     * @param {Int8Array} messageByteArray
     * @returns {Int8Array}
     */
    static heartBeat(messageByteArray: Int8Array): Int8Array;
    Receiver(): void;
}
import { InMemoryConnectionData } from '../../utils/connectionData/InMemoryConnectionData.js';
