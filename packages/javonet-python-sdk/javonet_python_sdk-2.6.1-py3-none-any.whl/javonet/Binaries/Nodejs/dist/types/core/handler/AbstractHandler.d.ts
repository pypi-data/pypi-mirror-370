export class AbstractHandler {
    /**
     * @type {Record<number, AbstractHandler>}
     */
    handlers: Record<number, AbstractHandler>;
    /**
     * @param {Command} command
     */
    process(command: Command): void;
    /**
     * @param {Command} command
     */
    handleCommand(command: Command): void;
    /**
     * @param {Command} command
     */
    iterate(command: Command): void;
    /**
     *
     * @param {*} error
     * @param {*} class_name
     * @returns
     */
    process_stack_trace(error: any, class_name: any): any;
}
import { Command } from '../../utils/Command.js';
