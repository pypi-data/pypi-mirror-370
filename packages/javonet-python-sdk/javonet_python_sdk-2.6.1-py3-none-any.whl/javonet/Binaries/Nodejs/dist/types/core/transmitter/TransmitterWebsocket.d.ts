/**
 * @typedef {import('../../utils/connectionData/IConnectionData.js').IConnectionData} IConnectionData
 */
export class TransmitterWebsocket {
    /**
     * @returns {void}
     */
    static initialize(): void;
    /**
     * @returns {void}
     */
    static setConfigSource(): void;
    /**
     * @returns {void}
     */
    static activate(): void;
    /**
     * @async
     * @param {Int8Array} messageByteArray
     * @param {IConnectionData} connectionData
     * @returns {Promise<Int8Array>} responseByteArray
     */
    static sendCommand(messageByteArray: Int8Array, connectionData: IConnectionData): Promise<Int8Array>;
}
export type IConnectionData = import("../../utils/connectionData/IConnectionData.js").IConnectionData;
