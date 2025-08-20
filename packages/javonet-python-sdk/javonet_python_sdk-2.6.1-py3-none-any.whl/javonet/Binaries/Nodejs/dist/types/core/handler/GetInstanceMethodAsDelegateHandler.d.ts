/**
 * Handles retrieving an instance method as a delegate.
 */
export class GetInstanceMethodAsDelegateHandler extends AbstractHandler {
    /** @type {Function|null} */
    method: Function | null;
    /** @type {number} */
    requiredParametersCount: number;
    /** @type {Array<*>} */
    args: Array<any>;
    /** @type {Object|null} */
    instance: Object | null;
    /**
     * Processes a command to retrieve an instance method as a delegate.
     * @param {Object} command - The command containing payload data.
     * @param {Array<*>} command.payload - The payload containing instance, method name, and arguments.
     * @returns {Function} The delegate for the instance method.
     * @throws {Error} If the parameters mismatch or the method cannot be found.
     */
    process(command: {
        payload: Array<any>;
    }): Function;
    /**
     * Retrieves the method from the type.
     * @param {Object} type - The class or constructor to search for the method.
     * @param {string} methodName - The name of the method.
     * @returns {Function|null} The found method or null if not found.
     */
    getMethod(type: Object, methodName: string): Function | null;
    /**
     * Creates an error message when the method is not found.
     * @param {Object} type - The class or constructor.
     * @param {string} methodName - The method name.
     * @returns {Error} The error with detailed message.
     */
    createMethodNotFoundError(type: Object, methodName: string): Error;
}
import { AbstractHandler } from './AbstractHandler.js';
