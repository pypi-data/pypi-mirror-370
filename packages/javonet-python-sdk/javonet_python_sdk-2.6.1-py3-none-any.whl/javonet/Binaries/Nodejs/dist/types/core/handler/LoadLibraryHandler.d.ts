export type Command = import("../../utils/Command.js").Command;
export class LoadLibraryHandler extends AbstractHandler {
    /** @type {string[]} */
    static loadedLibraries: string[];
    requiredParametersCount: number;
    /**
     * @param {Command} command
     */
    process(command: Command): number;
    getLoadedLibraries(): string[];
}
import { AbstractHandler } from './AbstractHandler.js';
