export class ActivationHelper {
    /** @type {string} */
    static temporaryLicenseKey: string;
    /**
     * @param {string} value
     */
    static setTemporaryLicenseKey(value: string): void;
    /**
     * @returns {string}
     */
    static getTemporaryLicenseKey(): string;
    /**
     * @returns {Promise<string>}
     */
    static getLicenseKey(): Promise<string>;
    /**
     * @returns {string}
     */
    static _getLicenseKeyFromFile(): string;
}
