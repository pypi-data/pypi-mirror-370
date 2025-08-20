export type Command = import("../../utils/Command.js").Command;
/**
 * @typedef {import('../../utils/Command.js').Command} Command
 */
export class ArrayHandler extends AbstractHandler {
    /**
     * @param {Command} command
     */
    process(command: Command): any;
}
import { AbstractHandler } from './AbstractHandler.js';
