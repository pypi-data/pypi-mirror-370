export type ConnectionType = any;
/**
 * @typedef {import('../ConnectionType.js').ConnectionType} ConnectionType
 */
/**
 * Represents WebSocket connection data.
 * @extends IConnectionData
 */
export class WsConnectionData extends IConnectionData {
    /**
     * @param {string} hostname - The hostname of the connection.
     */
    constructor(hostname: string);
    /** @private @type {string} */
    private _hostname;
    /** @private @type {ConnectionType} */
    private _connectionType;
    /** @type {string} */
    set hostname(value: string);
    /** @type {string} */
    get hostname(): string;
    /**
     * @param {WsConnectionData} other
     * @returns {boolean}
     */
    equals(other: WsConnectionData): boolean;
}
import { IConnectionData } from './IConnectionData.js';
