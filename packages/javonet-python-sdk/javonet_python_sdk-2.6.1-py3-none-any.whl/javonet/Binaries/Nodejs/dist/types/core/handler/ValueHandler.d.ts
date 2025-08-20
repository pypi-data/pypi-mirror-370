export type Command = import("../../utils/Command.js").Command;
/**
 * @typedef {import('../../utils/Command.js').Command} Command
 */
export class ValueHandler extends AbstractHandler {
    /**
     * @param {Command} command
     * @returns {unknown}
     */
    process(command: Command): unknown;
}
import { AbstractHandler } from './AbstractHandler.js';
