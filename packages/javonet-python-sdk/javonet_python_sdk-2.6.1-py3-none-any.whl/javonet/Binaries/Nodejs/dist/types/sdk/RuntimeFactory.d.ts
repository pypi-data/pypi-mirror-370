/**
 * @typedef {import('../utils/connectionData/IConnectionData.js').IConnectionData} IConnectionData
 */
/**
 * The RuntimeFactory class provides methods for creating runtime contexts.
 * Each method corresponds to a specific runtime (CLR, JVM, .NET Core, Perl, Ruby, Node.js, Python) and returns a RuntimeContext instance for that runtime.
 * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
 */
export class RuntimeFactory {
    /**
     * @param {IConnectionData} connectionData
     */
    constructor(connectionData: IConnectionData);
    connectionData: import("../utils/connectionData/IConnectionData.js").IConnectionData;
    /**
     * Creates RuntimeContext instance to interact with the .NET Framework runtime.
     * @return {RuntimeContext} a RuntimeContext instance for the .NET Framework runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    clr(): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with the JVM runtime.
     * @return {RuntimeContext} a RuntimeContext instance for the JVM runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    jvm(): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with the .NET runtime.
     * @return {RuntimeContext} a RuntimeContext instance for the .NET runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    netcore(): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with the Perl runtime.
     * @return {RuntimeContext} a RuntimeContext instance for the Perl runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    perl(): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with the Python runtime.
     * @return {RuntimeContext} a RuntimeContext instance for the Python runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    python(): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with the Ruby runtime.
     * @return {RuntimeContext} a RuntimeContext instance for the Ruby runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    ruby(): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with Node.js runtime.
     * @return {RuntimeContext} a RuntimeContext instance for the Node.js runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    nodejs(): RuntimeContext;
    /**
     * Creates RuntimeContext instance to interact with the Python runtime.
     * @return {RuntimeContext} a RuntimeContext instance for the Python runtime
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/runtime-context)
     */
    python27(): RuntimeContext;
}
export type IConnectionData = import("../utils/connectionData/IConnectionData.js").IConnectionData;
import { RuntimeContext } from './RuntimeContext.js';
