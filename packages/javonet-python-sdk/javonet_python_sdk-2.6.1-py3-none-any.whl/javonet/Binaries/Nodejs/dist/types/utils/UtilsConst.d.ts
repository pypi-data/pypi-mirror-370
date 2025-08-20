export class UtilsConst {
    /** @type {string} */
    static _javonetWorkingDirectory: string;
    /** @type {string} */
    static _configSource: string;
    /** @type {string} */
    static _licenseKey: string;
    /**
     * @param {string} inputPath
     */
    static setJavonetWorkingDirectory(inputPath: string): void;
    /**
     * @returns {string}
     */
    static getJavonetWorkingDirectory(): string;
    /**
     * @param {string} value
     */
    static setConfigSource(value: string): void;
    /**
     * @returns {string}
     */
    static getConfigSource(): string;
    /**
     * @param {string} value
     */
    static setLicenseKey(value: string): void;
    /**
     * @returns {string}
     */
    static getLicenseKey(): string;
}
