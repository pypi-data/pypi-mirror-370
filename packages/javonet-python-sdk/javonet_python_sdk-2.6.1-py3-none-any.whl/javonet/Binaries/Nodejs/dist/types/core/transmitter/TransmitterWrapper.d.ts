export class TransmitterWrapper {
    static isNativeLibraryLoaded(): boolean;
    static loadNativeLibrary(): void;
    /**
     * @param {string} licenseKey
     */
    static activate(licenseKey: string): any;
    /**
     * @param {Int8Array} messageArray
     */
    static sendCommand(messageArray: Int8Array): any;
    /**
     * @param {string} configSource
     */
    static setConfigSource(configSource: string): any;
    /**
     * @param {string} path
     */
    static setJavonetWorkingDirectory(path: string): void;
}
