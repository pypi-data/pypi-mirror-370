export type Command = import("../../utils/Command.js").Command;
/**
 * @typedef {import('../../utils/Command.js').Command} Command
 */
export class GetGlobalStaticFieldHandler extends AbstractHandler {
    requiredParametersCount: number;
    /**
     * @param {Command} command
     */
    process(command: Command): any;
}
import { AbstractHandler } from './AbstractHandler.js';
