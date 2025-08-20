export type RuntimeNameType = import("../types.d.ts").RuntimeName;
export type IConnectionData = import("../utils/connectionData/IConnectionData.js").IConnectionData;
export type Transmitter = typeof import("../core/transmitter/Transmitter.js").Transmitter;
/**
 * Represents a single context which allows interaction with a selected technology.
 * Refers to a single instance of the called runtime within a particular target OS process.
 * This can be either the local currently running process (inMemory) or a particular remote process identified by the IP Address and PORT of the target Javonet instance.
 * Multiple Runtime Contexts can be initialized within one process.
 * Calling the same technology on inMemory communication channel will return the existing instance of runtime context.
 * Calling the same technology on TCP channel but on different nodes will result in unique Runtime Contexts.
 * Within the runtime context, any number of libraries can be loaded and any objects from the target technology can be interacted with, as they are aware of each other due to sharing the same memory space and same runtime instance.
 * @see [Javonet Guides]{@link https://www.javonet.com/guides/v2/javascript/foundations/runtime-context}
 * @class
 */
export class RuntimeContext {
    /** @type {Map<string, RuntimeContext>} */
    static memoryRuntimeContexts: Map<string, RuntimeContext>;
    /** @type {Map<string, RuntimeContext>} */
    static networkRuntimeContexts: Map<string, RuntimeContext>;
    /** @type {Map<string, RuntimeContext>} */
    static webSocketRuntimeContexts: Map<string, RuntimeContext>;
    /**
     * @param {RuntimeNameType} runtimeName
     * @param {IConnectionData} connectionData
     * @returns {RuntimeContext}
     */
    static getInstance(runtimeName: RuntimeNameType, connectionData: IConnectionData): RuntimeContext;
    /**
     * @param {RuntimeNameType} runtimeName
     * @param {IConnectionData} connectionData
     */
    constructor(runtimeName: RuntimeNameType, connectionData: IConnectionData);
    _isExecuted: boolean;
    runtimeName: import("../types.d.ts").RuntimeName;
    connectionData: import("../utils/connectionData/IConnectionData.js").IConnectionData;
    /**
     * Executes the current command. The initial state of RuntimeContext is non-materialized,
     * wrapping either a single command or a chain of recursively nested commands.
     * Commands become nested through each invocation of methods on RuntimeContext.
     * Each invocation triggers the creation of a new RuntimeContext instance wrapping the current command with a new parent command.
     * The developer can decide at any moment of the materialization for the context, taking full control of the chunks of the expression being transferred and processed on the target runtime.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/execute-method)
     * @method
     */
    execute(): void;
    /**
     * Adds a reference to a library. Javonet allows you to reference and use modules or packages written in various languages.
     * This method allows you to use any library from all supported technologies. The necessary libraries need to be referenced.
     * The argument is a relative or full path to the library. If the library has dependencies on other libraries, the latter needs to be added first.
     * After referencing the library, any objects stored in this package can be used. Use static classes, create instances, call methods, use fields and properties, and much more.
     * @param {string} libraryPath - The relative or full path to the library.
     * @returns {RuntimeContext} RuntimeContext instance.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/getting-started/adding-references-to-libraries)
     * @method
     */
    loadLibrary(libraryPath: string): RuntimeContext;
    /**
     * Retrieves a reference to a specific type. The type can be a class, interface or enum. The type can be retrieved from any referenced library.
     * @param {string} typeName - The full name of the type.
     * @param {...any} args - The arguments to be passed, if needed
     * @returns {InvocationContext} InvocationContext instance, that wraps the command to get the type.
     * @method
     */
    getType(typeName: string, ...args: any[]): InvocationContext;
    /**
     * Casts the provided value to a specific type. This method is used when invoking methods that require specific types of arguments.
     * The arguments include the target type and the value to be cast. The target type must be retrieved from the called runtime using the getType method.
     * After casting the value, it can be used as an argument when invoking methods.
     * @param {...any} args - The target type and the value to be cast.
     * @returns {InvocationContext} InvocationContext instance that wraps the command to cast the value.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/casting/casting)
     * @method
     */
    cast(...args: any[]): InvocationContext;
    /**
     * Retrieves a specific item from an enum type. This method is used when working with enums from the called runtime.
     * The arguments include the enum type and the name of the item. The enum type must be retrieved from the called runtime using the getType method.
     * After retrieving the item, it can be used as an argument when invoking methods or for other operations.
     * @param {...any} args - The enum type and the name of the item.
     * @returns {InvocationContext} InvocationContext instance that wraps the command to get the enum item.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/enums/using-enum-type)
     * @method
     */
    getEnumItem(...args: any[]): InvocationContext;
    /**
     * Creates a reference type argument that can be passed to a method with a ref parameter modifier. This method is used when working with methods from the called runtime that require arguments to be passed by reference.
     * The arguments include the value and optionally the type of the reference. The type must be retrieved from the called runtime using the getType method.
     * After creating the reference, it can be used as an argument when invoking methods.
     * @param {...any} args - The value and optionally the type of the reference.
     * @returns {InvocationContext} InvocationContext instance that wraps the command to create a reference as ref.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/methods-arguments/passing-arguments-by-reference-with-ref-keyword)
     * @method
     */
    asRef(...args: any[]): InvocationContext;
    /**
     * Creates a reference type argument that can be passed to a method with an out parameter modifier. This method is used when working with methods from the called runtime that require arguments to be passed by reference.
     * The arguments include the value and optionally the type of the reference. The type must be retrieved from the called runtime using the getType method.
     * After creating the reference, it can be used as an argument when invoking methods.
     * @param {...any} args - The value and optionally the type of the reference.
     * @returns {InvocationContext} InvocationContext instance that wraps the command to create a reference as out.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/methods-arguments/passing-arguments-by-reference-with-out-keyword |Passing Arguments by Reference with out Keyword Guide)
     * @method
     */
    asOut(...args: any[]): InvocationContext;
    /**
     * Invokes a function from the called runtime. This method is used when working with functions from the called runtime.
     * The arguments include the function name and the arguments to be passed to the function.
     * After invoking the function, the result can be used for further operations.
     * @param {string} functionName - The name of the function to invoke.
     * @param {...any} args - The arguments to be passed to the function.
     * @returns {InvocationContext} InvocationContext instance that wraps the command to invoke the function.
     * @see [Invoking Functions Guide](https://www.javonet.com/guides/v2/csharp/functions/invoking-functions)
     * @method
     */
    invokeGlobalFunction(functionName: string, ...args: any[]): InvocationContext;
    healthCheck(): void;
    #private;
}
import { InvocationContext } from './InvocationContext.js';
