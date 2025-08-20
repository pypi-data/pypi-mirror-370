export class TypeCache {
    /** @type {TypeCache | null} */
    static _instance: TypeCache | null;
    /** @type {string[]} */
    typeCache: string[];
    /**
     * @param {string} typRegex
     */
    cacheType(typRegex: string): void;
    isTypeCacheEmpty(): boolean;
    /**
     * @param {{ name: string }} typeToCheck
     */
    isTypeAllowed(typeToCheck: {
        name: string;
    }): boolean;
    getCachedTypes(): string[];
    clearCache(): number;
}
