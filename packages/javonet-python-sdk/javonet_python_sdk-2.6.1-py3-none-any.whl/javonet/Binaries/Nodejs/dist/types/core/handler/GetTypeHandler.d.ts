export type Command = import("../../utils/Command.js").Command;
/**
 * @typedef {import('../../utils/Command.js').Command} Command
 */
export class GetTypeHandler extends AbstractHandler {
    /** @type {number} */
    requiredParametersCount: number;
    /** @type {NamespaceCache} */
    namespaceCache: NamespaceCache;
    /** @type {TypeCache} */
    typeCache: TypeCache;
    /** @type {LoadLibraryHandler} */
    loadLibaryHandler: LoadLibraryHandler;
    /**
     *
     * @param {Command} command
     * @returns
     */
    process(command: Command): any;
    getAvailableTypes(): string[];
}
import { AbstractHandler } from './AbstractHandler.js';
import { NamespaceCache } from '../namespaceCache/NamespaceCache.js';
import { TypeCache } from '../typeCache/TypeCache.js';
import { LoadLibraryHandler } from './LoadLibraryHandler.js';
