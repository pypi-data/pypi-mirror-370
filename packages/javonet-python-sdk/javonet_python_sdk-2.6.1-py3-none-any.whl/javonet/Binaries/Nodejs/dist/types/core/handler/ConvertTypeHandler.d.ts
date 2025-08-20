export type Command = import("../../utils/Command.js").Command;
/**
 * @typedef {import('../../utils/Command.js').Command} Command
 */
/**
 * ConvertTypeHandler class handles the conversion of JType to Type.
 */
export class ConvertTypeHandler extends AbstractHandler {
    /**
     * Minimum required parameters count for the command.
     * @type {number}
     */
    requiredParametersCount: number;
    /**
     * Processes the given command to convert JType to Type.
     * @param {Command} command - The command to process.
     * @returns {any} The converted type.
     */
    process(command: Command): any;
    /**
     * Validates the command to ensure it has enough parameters.
     * @param {Command} command - The command to validate.
     */
    validateCommand(command: Command): void;
}
import { AbstractHandler } from './AbstractHandler.js';
