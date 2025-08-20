export type Cache = {
    [x: string]: any;
};
export class ReferencesCache {
    /**
     * @returns {ReferencesCache}
     */
    static getInstance(): ReferencesCache;
    /**
     * @param {any} reference
     * @returns {string}
     */
    cacheReference(reference: any): string;
    /**
     * @param {string} id
     * @returns {any}
     */
    resolveReference(id: string): any;
    /**
     * @param {string} id
     * @returns {number}
     */
    deleteReference(id: string): number;
}
