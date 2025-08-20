export class NamespaceCache {
    /** @type {NamespaceCache | null} */
    static _instance: NamespaceCache | null;
    /** @type {string[]} */
    namespaceCache: string[];
    /**
     * @param {string} namespaceRegex
     */
    cacheNamespace(namespaceRegex: string): void;
    /**
     * @returns {boolean}
     */
    isNamespaceCacheEmpty(): boolean;
    /**
     * @param {string} typeToCheck
     * @returns {boolean}
     */
    isTypeAllowed(typeToCheck: string): boolean;
    getCachedNamespaces(): string[];
    clearCache(): number;
}
