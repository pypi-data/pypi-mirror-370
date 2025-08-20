export type RuntimeNameType = import("../types.d.ts").RuntimeName;
export type IConnectionData = import("../utils/connectionData/IConnectionData.js").IConnectionData;
/**
 * @typedef {import('../types.d.ts').RuntimeName} RuntimeNameType
 * @typedef {import('../utils/connectionData/IConnectionData.js').IConnectionData} IConnectionData
 */
/**
 * InvocationContext is a class that represents a context for invoking commands.
 * It implements several interfaces for different types of interactions.
 * This class is used to construct chains of invocations, representing expressions of interaction that have not yet been executed.
 * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/invocation-context)
 * @class
 */
export class InvocationContext {
    /**
     *
     * @param {RuntimeNameType} runtimeName
     * @param {IConnectionData} connectionData
     * @param {Command} command
     * @param {boolean} isExecuted
     */
    constructor(runtimeName: RuntimeNameType, connectionData: IConnectionData, command: Command, isExecuted?: boolean);
    /**
     * @returns {Command|null}
     */
    get_current_command(): Command | null;
    /**
     * Executes the current command.
     * Because invocation context is building the intent of executing particular expression on target environment, we call the initial state of invocation context as non-materialized.
     * The non-materialized context wraps either single command or chain of recursively nested commands.
     * Commands are becoming nested through each invocation of methods on Invocation Context.
     * Each invocation triggers the creation of new Invocation Context instance wrapping the current command with new parent command valid for invoked method.
     * Developer can decide on any moment of the materialization for the context taking full control of the chunks of the expression being transferred and processed on target runtime.
     * @returns {InvocationContext} the InvocationContext after executing the command.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/execute-method)
     * @method
     */
    execute(): InvocationContext;
    /**
     * Invokes a static method on the target runtime.
     * @param {string} methodName - The name of the method to invoke.
     * @param {...any} args - Method arguments.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to invoke the static method.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/calling-methods/invoking-static-method)
     * @method
     */
    invokeStaticMethod(methodName: string, ...args: any[]): InvocationContext;
    /**
     * Retrieves the value of a static field from the target runtime.
     * @param {string} fieldName - The name of the field to get.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to get the static field.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/fields-and-properties/getting-and-setting-values-for-static-fields-and-properties)
     * @method
     */
    getStaticField(fieldName: string): InvocationContext;
    /**
     * Sets the value of a static field in the target runtime.
     * @param {string} fieldName - The name of the field to set.
     * @param {any} value - The new value of the field.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to set the static field.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/fields-and-properties/getting-and-setting-values-for-static-fields-and-properties)
     * @method
     */
    setStaticField(fieldName: string, value: any): InvocationContext;
    /**
     * Creates a new instance of a class in the target runtime.
     * @param {...any} args - The arguments to pass to the class constructor
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to create the instance.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/calling-methods/creating-instance-and-calling-instance-methods)
     * @method
     */
    createInstance(...args: any[]): InvocationContext;
    /**
     * Retrieves the value of an instance field from the target runtime.
     * @param {string} fieldName - The name of the field to get.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to get the instance field.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/fields-and-properties/getting-and-setting-values-for-instance-fields-and-properties)
     * @method
     */
    getInstanceField(fieldName: string): InvocationContext;
    /**
     * Sets the value of an instance field in the target runtime.
     * @param {string} fieldName - The name of the field to set.
     * @param {any} value - The new value of the field.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to set the instance field.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/fields-and-properties/getting-and-setting-values-for-instance-fields-and-properties)
     * @method
     */
    setInstanceField(fieldName: string, value: any): InvocationContext;
    /**
     * Invokes an instance method on the target runtime.
     * @param {string} methodName - The name of the method to invoke.
     * @param {...any} args - Method arguments.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to invoke the instance method.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/calling-methods/invoking-instance-method)
     * @method
     */
    invokeInstanceMethod(methodName: string, ...args: any[]): InvocationContext;
    /**
     * Retrieves the value at a specific index in an array from the target runtime.
     * @param {...any} indexes - the arguments to pass to the array getter. The first argument should be the index.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to get the index.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/arrays-and-collections/one-dimensional-arrays)
     * @method
     */
    getIndex(...indexes: any[]): InvocationContext;
    /**
     * Sets the value at a specific index in an array in the target runtime.
     * @param {number[]} indexes - The index to set the value at.
     * @param {any} value - The value to set at the index.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to set the index.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/arrays-and-collections/one-dimensional-arrays)
     * @method
     */
    setIndex(indexes: number[], value: any): InvocationContext;
    /**
     * Retrieves the size of an array from the target runtime.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to get the size.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/arrays-and-collections/one-dimensional-arrays)
     * @method
     */
    getSize(): InvocationContext;
    /**
     * Retrieves the rank of an array from the target runtime.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to get the rank.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/arrays-and-collections/one-dimensional-arrays)
     * @method
     */
    getRank(): InvocationContext;
    /**
     * Invokes a generic static method on the target runtime.
     * @param {string} methodName - The name of the method to invoke.
     * @param {...any} args - Method arguments.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to invoke the generic static method.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/generics/calling-generic-static-method)
     * @method
     */
    invokeGenericStaticMethod(methodName: string, ...args: any[]): InvocationContext;
    /**
     * Invokes a generic method on the target runtime.
     * @param {string} methodName - The name of the method to invoke.
     * @param {...any} args - Method arguments.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to invoke the generic method.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/generics/calling-generic-instance-method)
     * @method
     */
    invokeGenericMethod(methodName: string, ...args: any[]): InvocationContext;
    /**
     * Retrieves the name of an enum from the target runtime.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to get the enum name.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/enums/using-enum-type)
     * @method
     */
    getEnumName(): InvocationContext;
    /**
     * Retrieves the value of an enum from the target runtime.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to get the enum value.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/enums/using-enum-type)
     * @method
     */
    getEnumValue(): InvocationContext;
    /**
     * Retrieves the value of a reference from the target runtime.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to get the ref value.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/methods-arguments/passing-arguments-by-reference-with-ref-keyword)
     * @method
     */
    getRefValue(): InvocationContext;
    /**
     * Creates a null object of a specific type on the target runtime.
     *
     * @returns {InvocationContext} An InvocationContext instance with the command to create a null object.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/null-handling/create-null-object)
     * @method
     */
    createNull(): InvocationContext;
    /**
     * Creates a null object of a specific type on the target runtime.
     * @param {string} methodName - The name of the method to invoke.
     * @param {...any} args - Method arguments.
     * @returns {InvocationContext} An InvocationContext instance with the command to create a null object.
     * TODO: connect documentation page url
     * @see [Javonet Guides](https://www.javonet.com/guides/)
     * @method
     */
    getStaticMethodAsDelegate(methodName: string, ...args: any[]): InvocationContext;
    /**
     * Creates a null object of a specific type on the target runtime.
     * @param {string} methodName - The name of the method to invoke.
     * @param {...any} args - Method arguments.
     * @returns {InvocationContext|InvocationWsContext} An InvocationContext instance with the command to create a null object.
     * TODO: connect documentation page url
     * @see [Javonet Guides](https://www.javonet.com/guides/)
     * @method
     */
    getInstanceMethodAsDelegate(methodName: string, ...args: any[]): InvocationContext | InvocationWsContext;
    /**
     * Retrieves an array from the target runtime.
     * @returns {InvocationContext} A new InvocationContext instance that wraps the command to retrieve the array.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/arrays-and-collections/retrieve-array)
     * @method
     */
    retrieveArray(): InvocationContext;
    /**
     * Returns the primitive value from the target runtime. This could be any primitive type in JavaScript,
     * such as int, boolean, byte, char, long, double, float, etc.
     * @returns {Command} The value of the current command.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/execute-method)
     * @method
     */
    /**
     * @returns {unknown}
     */
    getValue(): unknown;
    [Symbol.iterator]: () => {
        next: () => {
            value: InvocationContext;
            done: boolean;
        };
    };
    #private;
}
export class InvocationWsContext extends InvocationContext {
    /**
     * Executes the current command.
     * Because invocation context is building the intent of executing particular expression on target environment, we call the initial state of invocation context as non-materialized.
     * The non-materialized context wraps either single command or chain of recursively nested commands.
     * Commands are becoming nested through each invocation of methods on Invocation Context.
     * Each invocation triggers the creation of new Invocation Context instance wrapping the current command with new parent command valid for invoked method.
     * Developer can decide on any moment of the materialization for the context taking full control of the chunks of the expression being transferred and processed on target runtime.
     * @returns {Promise<InvocationWsContext>} the InvocationContext after executing the command.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/execute-method)
     * @async
     * @method
     */
    execute(): Promise<InvocationWsContext>;
    #private;
}
import { Command } from '../utils/Command.js';
