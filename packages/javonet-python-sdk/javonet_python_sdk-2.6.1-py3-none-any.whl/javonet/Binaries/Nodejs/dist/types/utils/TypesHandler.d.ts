/**
 * TypesHandler class provides utilities for converting between types.
 */
export class TypesHandler {
    /**
     * Converts a JavaScript type to a JType equivalent.
     * @param {Function} type - The JavaScript type.
     * @returns {string} The corresponding type name
     */
    static convertTypeToJType(type: Function): string;
    /**
     * @param {unknown} value
     * @returns {boolean}
     */
    static isPrimitiveOrNullOrUndefined(value: unknown): boolean;
}
