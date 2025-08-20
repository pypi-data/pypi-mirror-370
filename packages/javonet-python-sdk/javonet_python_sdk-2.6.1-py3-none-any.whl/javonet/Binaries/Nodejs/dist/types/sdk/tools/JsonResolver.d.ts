export type RuntimeChannelType = import("../../types.d.ts").RuntimeChannelType;
export type ConfigSource = import("../../types.d.ts").ConfigSource;
export type RuntimeChannel = import("../../types.d.ts").RuntimeChannel;
export type Runtime = import("../../types.d.ts").Runtime;
export type Runtimes = import("../../types.d.ts").Runtimes;
export type RuntimeType = import("../../types.d.ts").RuntimeType;
export class JsonResolver {
    /**
     * @param {string | ConfigSource} configSource
     */
    constructor(configSource: string | ConfigSource);
    /** @type {ConfigSource} */
    jsonObject: ConfigSource;
    /** @type {string | ConfigSource} */
    configSource: string | ConfigSource;
    /**
     * @returns {Partial<Runtimes>}
     */
    get runtimes(): Partial<Runtimes>;
    /**
     * @returns {string}
     */
    get licenseKey(): string;
    /**
     * @returns {string}
     */
    get workingDirectory(): string;
    /**
     * @returns {string}
     */
    getLicenseKey(): string;
    /**
     * @returns {string}
     */
    getWorkingDirectory(): string;
    /**
     * @param {RuntimeType} runtimeName
     * @param {string} configName
     * @returns {RuntimeChannelType}
     */
    getChannelType(runtimeName: RuntimeType, configName: string): RuntimeChannelType;
    /**
     * @param {RuntimeType} runtimeName
     * @param {string} configName
     * @returns {string}
     */
    getChannelHost(runtimeName: RuntimeType, configName: string): string;
    /**
     * @param {RuntimeType} runtimeName
     * @param {string} configName
     * @returns {number|string}
     */
    getChannelPort(runtimeName: RuntimeType, configName: string): number | string;
    /**
     * @param {RuntimeType} runtimeName
     * @param {string} configName
     * @returns {string}
     */
    getModules(runtimeName: RuntimeType, configName: string): string;
    /**
     * @private
     * @param {string | ConfigSource} configSource
     * @returns {ConfigSource}
     */
    private _getJsonObject;
    /**
     * @private
     * @param {RuntimeType} runtimeName
     * @param {string} configName
     * @returns {Runtime}
     */
    private _getRuntime;
    /**
     * @private
     * @param {RuntimeType} runtimeName
     * @param {string} configName
     * @returns {string}
     */
    private _getRuntimeName;
    /**
     * @private
     * @param {RuntimeType} runtimeName
     * @param {string} configName
     * @returns {RuntimeChannel}
     */
    private _getChannel;
}
