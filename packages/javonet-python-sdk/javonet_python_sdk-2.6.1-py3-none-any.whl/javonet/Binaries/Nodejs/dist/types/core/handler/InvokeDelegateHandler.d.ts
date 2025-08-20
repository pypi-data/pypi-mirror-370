export type Command = import("../../utils/Command.js").Command;
/**
 * @typedef {import('../../utils/Command.js').Command} Command
 */
/**
 * Handles invoking a delegate by GUID.
 */
export class InvokeDelegateHandler extends AbstractHandler {
    /** @type {number} */
    requiredParametersCount: number;
    /**
     * Processes a command to invoke a delegate.
     * @param {Command} command - The command containing payload data.
     * @returns {*} The result of the delegate invocation.
     * @throws {Error} If the parameters mismatch or the delegate cannot be found.
     */
    process(command: Command): any;
}
import { AbstractHandler } from './AbstractHandler.js';
