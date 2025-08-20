export type Command = import("../../utils/Command.js").Command;
export type Interpreter = import("../interpreter/Interpreter.js").Interpreter;
/**
 * @typedef {import('../../utils/Command.js').Command} Command
 * @typedef {import('../interpreter/Interpreter.js').Interpreter} Interpreter
 */
/**
 * PassDelegateHandler class responsible for processing a command to create a delegate.
 */
export class PassDelegateHandler extends AbstractHandler {
    constructor(interpreter?: null);
    /** @type {Interpreter | null | undefined} */
    interpreter: Interpreter | null | undefined;
    /**
     * Minimum required parameters count for the command.
     * @type {number}
     */
    requiredParametersCount: number;
    /**S
     * Processes the given command to create and compile a delegate.
     * @param {Command} command - The command to process.
     * @returns {Function} The compiled delegate function.
     */
    process(command: Command): Function;
    /**
     * Validates the command to ensure it has enough parameters.
     * @param {Command} command - The command to validate.
     */
    validateCommand(command: Command): void;
    /**
     * Retrieves the arguments from the command payload.
     * @param {Command} command - The command containing the payload.
     * @returns {Array<any>} The extracted arguments.
     */
    getArguments(command: Command): Array<any>;
    /**
     * Extracts argument types from the arguments array.
     * @param {Array<any>} args - The arguments array.
     * @returns {Array<any>} The argument types.
     */
    getArgumentTypes(args: Array<any>): Array<any>;
    /**
     * Retrieves the return type from the arguments array.
     * @param {Array<any>} args - The arguments array.
     * @returns {Function} The return type.
     */
    getReturnType(args: Array<any>): Function;
    /**
     * Creates parameter expressions from argument types.
     * @param {Array<any>} argsTypes - The argument types.
     * @returns {Array<any>} The parameter expressions.
     */
    createParameters(argsTypes: Array<any>): Array<any>;
    /**
     * Creates an array of arguments for the delegate.
     * @param {string} delegateGuid - The delegate identifier.
     * @param {Array<any>} parameters - The parameter expressions.
     * @returns {Array<any>} The arguments array.
     */
    createArgsArray(delegateGuid: string, parameters: Array<any>): Array<any>;
    /**
     * Creates a command expression.
     * @param {string} callingRuntimeName - The runtime name.
     * @param {Array<any>} payload - The arguments array.
     * @returns {Object} The command object.
     */
    createCommand(callingRuntimeName: string, payload: Array<any>): Object;
    /**
     * Creates a method call to execute the command.
     * @param {Command} command - The command object.
     * @returns {any} The response object.
     */
    createExecuteCall(command: Command): any;
    /**
     * Retrieves the response payload from the execution call.
     * @param {Object<string, any>} executeCall - Object containing the execution call.
     * @returns {Array<any>} The response payload.
     */
    getResponse(executeCall: {
        [x: string]: any;
    }): Array<any>;
    /**
     * Converts the first element of the response to the return type.
     * @param {Array<any>} response - The response payload.
     * @param {Function} returnType - The return type.
     * @returns {*} The converted first element.
     */
    convertFirstElement(response: Array<any>, returnType: Function): any;
    /**
     * Creates a block of expressions for the delegate.
     * @param {Function} returnType - The return type.
     * @param {*} convertedFirstElement - The converted first element.
     * @returns {Object} The block expression.
     */
    createBlock(returnType: Function, convertedFirstElement: any): Object;
    /**
     * Creates a delegate type.
     * @param {Array<any>} parameters - The parameter expressions.
     * @param {Function} returnType - The return type.
     * @returns {Function} The delegate type.
     */
    createDelegateType(parameters: Array<any>, returnType: Function): Function;
}
import { AbstractHandler } from './AbstractHandler.js';
