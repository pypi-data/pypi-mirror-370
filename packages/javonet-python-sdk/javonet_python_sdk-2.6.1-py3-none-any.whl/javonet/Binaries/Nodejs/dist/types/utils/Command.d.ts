/**
 * @typedef {import('../types.d.ts').RuntimeName} RuntimeName
 */
export class Command {
    /**
     * @param {unknown} response
     * @param {RuntimeName} runtimeName
     * @returns {Command}
     */
    static createResponse(response: unknown, runtimeName: RuntimeName): Command;
    /**
     * @param {unknown} response
     * @param {RuntimeName} runtimeName
     * @returns {Command}
     */
    static createReference(response: unknown, runtimeName: RuntimeName): Command;
    /**
     * @param {unknown} response
     * @param {RuntimeName} runtimeName
     * @returns {Command}
     */
    static createArrayResponse(response: unknown, runtimeName: RuntimeName): Command;
    /**
     * Constructs a new Command instance.
     * @param {RuntimeName} runtimeName - The runtime name associated with the command.
     * @param {number} commandType - The type of the command.
     * @param {any} [payload] - The optional payload of the command.
     * @method
     */
    constructor(runtimeName: RuntimeName, commandType: number, payload?: any);
    runtimeName: import("../types.d.ts").RuntimeName;
    commandType: number;
    payload: any;
    dropFirstPayloadArg(): Command;
    /**
     * @param {any} arg
     * @returns {Command}
     */
    addArgToPayload(arg: any): Command;
    /**
     * @param {Command|null} current_command
     * @returns {Command}
     */
    prependArgToPayload(current_command: Command | null): Command;
}
export type RuntimeName = import("../types.d.ts").RuntimeName;
