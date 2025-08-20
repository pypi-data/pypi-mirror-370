export type Command = import("../../utils/Command.js").Command;
/**
 * @typedef {import('../../utils/Command.js').Command} Command
 */
export class ArrayGetSizeHandler extends AbstractHandler {
    requiredParametersCount: number;
    /**
     * @param {Command} command
     */
    process(command: Command): number;
}
import { AbstractHandler } from './AbstractHandler.js';
