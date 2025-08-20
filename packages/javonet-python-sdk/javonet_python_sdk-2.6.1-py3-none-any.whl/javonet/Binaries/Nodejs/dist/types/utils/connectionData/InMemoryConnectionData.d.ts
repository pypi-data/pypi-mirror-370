export type ConnectionType = any;
/**
 * @typedef {import('../ConnectionType.js').ConnectionType} ConnectionType
 */
/**
 * @extends IConnectionData
 */
export class InMemoryConnectionData extends IConnectionData {
    _connectionType: 0;
    _hostname: string;
    /**
     * @param {InMemoryConnectionData} other
     * @returns {boolean}
     */
    equals(other: InMemoryConnectionData): boolean;
}
import { IConnectionData } from './IConnectionData.js';
