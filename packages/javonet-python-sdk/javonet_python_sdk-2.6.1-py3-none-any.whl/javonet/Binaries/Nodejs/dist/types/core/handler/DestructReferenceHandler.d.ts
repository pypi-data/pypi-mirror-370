export type Command = import("../../utils/Command.js").Command;
/**
 * @typedef {import('../../utils/Command.js').Command} Command
 */
export class DestructReferenceHandler extends AbstractHandler {
    /**
     * @param {Command} command
     */
    process(command: Command): number;
}
import { AbstractHandler } from './AbstractHandler.js';
