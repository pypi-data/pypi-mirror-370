export class RuntimeLoggerBrowser {
    static notLoggedYet: boolean;
    /**
     * Gets runtime information in a browser environment.
     * @method
     * @returns {string}
     */
    static getRuntimeInfo(): string;
    /**
     * Prints runtime information to the console.
     * @method
     * @returns {void}
     */
    static printRuntimeInfo(): void;
}
