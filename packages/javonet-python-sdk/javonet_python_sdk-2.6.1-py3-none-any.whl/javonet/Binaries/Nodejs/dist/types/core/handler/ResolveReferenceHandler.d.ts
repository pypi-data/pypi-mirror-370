export class ResolveReferenceHandler extends AbstractHandler {
    /**
     * @param {Command} command
     * @returns {any}
     */
    process(command: Command): any;
}
import { AbstractHandler } from './AbstractHandler.js';
import { Command } from '../../utils/Command.js';
