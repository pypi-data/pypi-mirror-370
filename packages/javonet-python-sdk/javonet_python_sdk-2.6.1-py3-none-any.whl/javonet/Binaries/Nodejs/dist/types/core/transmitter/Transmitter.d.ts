export class Transmitter {
    /**
     * @param {Int8Array} messageArray
     * @returns {Int8Array}
     */
    static sendCommand(messageArray: Int8Array): Int8Array;
    /**
     * @param {string} licenseKey
     * @returns {void}
     */
    static activate(licenseKey: string): void;
    /**
     * @param {string} configSource
     * @returns {void}
    */
    static setConfigSource(configSource: string): void;
    /**
     * @param {string} workingDirectory
     * @returns
     */
    static setJavonetWorkingDirectory(workingDirectory: string): void;
}
