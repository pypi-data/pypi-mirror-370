/**
 * @typedef {import('../ConnectionType.js').ConnectionType} ConnectionType
 */
export class IConnectionData {
    /**
     * @returns {ConnectionType}
     */
    get connectionType(): ConnectionType;
    /**
     * @returns {string}
     */
    get hostname(): string;
    /**
     * @returns {number[]}
     */
    serializeConnectionData(): number[];
}
export type ConnectionType = any;
