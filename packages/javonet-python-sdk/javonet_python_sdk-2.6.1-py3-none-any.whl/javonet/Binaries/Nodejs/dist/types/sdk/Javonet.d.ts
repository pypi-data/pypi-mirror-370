export type ConfigSource = import("../types.d.ts").ConfigSource;
/**
 * The Javonet class is a singleton class that serves as the entry point for interacting with Javonet.
 * It provides methods to activate and initialize the Javonet SDK.
 * It supports both in-memory and TCP connections.
 * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/javonet-static-class)
 */
export class Javonet {
    /**
     * Initializes Javonet using an in-memory channel on the same machine.
     * @returns {RuntimeFactory} A RuntimeFactory instance configured for an in-memory connection.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/in-memory-channel)
     */
    static inMemory(): RuntimeFactory;
    /**
     * Initializes Javonet with a TCP connection to a remote machine.
     * @param {TcpConnectionData} tcpConnectionData - The tcp connection data of the remote machine.
     * @returns {RuntimeFactory} A RuntimeFactory instance configured for a TCP connection.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/tcp-channel)
     */
    static tcp(tcpConnectionData: TcpConnectionData): RuntimeFactory;
    /**
     * Initializes Javonet with a WebSocket connection to a remote machine.
     * @param {WsConnectionData} wsConnectionData - The WebSocket connection data of the remote machine.
     * @returns {RuntimeFactory} A RuntimeFactory instance configured for a WebSocket connection.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/websocket-channel)
     */
    static webSocket(wsConnectionData: WsConnectionData): RuntimeFactory;
    /**
     * Initializes Javonet with a custom configuration file taken from external source.
     * Currentyl supported: Configuration file in JSON format
     * @param {string|ConfigSource} config - Path to a configuration file.
     * @returns {ConfigRuntimeFactory} A ConfigRuntimeFactory instance with configuration data.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/foundations/configure-channel)
     */
    static withConfig(config: string | ConfigSource): ConfigRuntimeFactory;
    /**
     * Activates Javonet with the provided license key.
     * @param {string} licenseKey - The license key to activate Javonet.
     * @returns {void} The activation status code.
     * @see [Javonet Guides](https://www.javonet.com/guides/v2/javascript/getting-started/activating-javonet)
     */
    static activate(licenseKey: string): void;
    /**
     * Gets the runtime information.
     * @returns {string} The runtime information.
     */
    static getRuntimeInfo(): string;
    /**
     * Sets the configuration source for the Javonet SDK.
     * @param {string} configSource - The configuration source.
     * @returns {void}
     */
    static setConfigSource(configSource: string): void;
    /**
     * Sets the working directory for the Javonet SDK.
     * @param {string} path - The working directory.
     * @returns {void}
     */
    static setJavonetWorkingDirectory(path: string): void;
}
import { TcpConnectionData } from '../utils/nodejs/connectionData/TcpConnectionData.js';
import { WsConnectionData } from '../utils/connectionData/WsConnectionData.js';
import { CommandSerializer } from '../core/protocol/CommandSerializer.js';
import { CommandDeserializer } from '../core/protocol/CommandDeserializer.js';
import { RuntimeFactory } from './RuntimeFactory.js';
import { ConfigRuntimeFactory } from './ConfigRuntimeFactory.js';
export { TcpConnectionData, WsConnectionData, CommandSerializer, CommandDeserializer };
