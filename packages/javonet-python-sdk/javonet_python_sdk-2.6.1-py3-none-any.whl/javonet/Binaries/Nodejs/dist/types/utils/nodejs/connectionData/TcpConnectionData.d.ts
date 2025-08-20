/**
 * @typedef {import('../../ConnectionType.js').ConnectionType} ConnectionType
 * @extends IConnectionData
 */
export class TcpConnectionData extends IConnectionData {
    /**
     * @param {string} hostname
     * @param {number} port
     */
    constructor(hostname: string, port: number);
    /** @type {string} */
    ipAddress: string;
    /** @type {number} */
    _port: number;
    /** @type {string} */
    _hostname: string;
    /** @type {ConnectionType} */
    _connectionType: ConnectionType;
    /**
     * @param {TcpConnectionData} other
     * @returns {boolean}
     */
    equals(other: TcpConnectionData): boolean;
    /**
     * @param {string} hostname
     * @returns {string}
     */
    resolveIpAddress(hostname: string): string;
    #private;
}
export type ConnectionType = any;
import { IConnectionData } from '../../connectionData/IConnectionData.js';
