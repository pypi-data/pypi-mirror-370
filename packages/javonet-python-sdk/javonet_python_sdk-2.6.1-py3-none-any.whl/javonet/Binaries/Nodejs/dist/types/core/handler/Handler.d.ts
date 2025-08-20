export type RuntimeName = import("../../types.d.ts").RuntimeName;
export class Handler {
    /**
     * @param {import('../interpreter/Interpreter.js').Interpreter} interpreter
     */
    constructor(interpreter: import("../interpreter/Interpreter.js").Interpreter);
    interpreter: import("../interpreter/Interpreter.js").Interpreter;
    /**
     * @param {Command} command
     */
    handleCommand(command: Command): Command;
    /**
     * @param {any} response
     * @param {RuntimeName} runtimeName
     * @returns {Command}
     */
    parseCommand(response: any, runtimeName: RuntimeName): Command;
}
/**
 * @typedef {import('../../types.d.ts').RuntimeName} RuntimeName
 */
/**
 * @type {Record<number, AbstractHandler>}
 */
export const handlers: Record<number, AbstractHandler>;
import { Command } from '../../utils/Command.js';
import { AbstractHandler } from './AbstractHandler.js';
