export class ReceiverNative {
    /**
     * @param {Int8Array} messageByteArray
     */
    static sendCommand(messageByteArray: Int8Array): Int8Array<ArrayBufferLike>;
    /**
     * @param {Int8Array} messageByteArray
     */
    static heartBeat(messageByteArray: Int8Array): Int8Array<ArrayBufferLike>;
}
