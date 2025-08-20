export const delegatesCacheInstance: DelegatesCache;
/**
 * A cache for storing and retrieving delegates.
 */
declare class DelegatesCache {
    cache: Map<any, any>;
    /**
     * Adds a delegate to the cache and returns its unique ID.
     * @param {Function} delegateInstance - The delegate function to store.
     * @returns {string} The unique ID for the delegate.
     */
    addDelegate(delegateInstance: Function): string;
    /**
     * Retrieves a delegate by its unique ID.
     * @param {string} delegateId - The unique ID of the delegate.
     * @returns {Function} The delegate function.
     * @throws {Error} If the delegate is not found.
     */
    getDelegate(delegateId: string): Function;
}
export {};
