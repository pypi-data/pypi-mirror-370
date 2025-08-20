export type Command = import("../../utils/Command.js").Command;
/**
 * @typedef {import('../../utils/Command.js').Command} Command
 */
export class EnableNamespaceHandler extends AbstractHandler {
    requiredParametersCount: number;
    /**
     * @param {Command} command
     */
    process(command: Command): number;
}
import { AbstractHandler } from './AbstractHandler.js';
