/**
 * Validate if the runtime is Node.js
 * @returns {boolean}
 */
export function isNodejsRuntime(): boolean;
/**
 * Validate if the runtime is Browser
 * @returns {boolean}
 */
export function isBrowserRuntime(): boolean;
/**
 * Validate if the runtime is ESM
 * @returns {boolean}
 */
export function isEsmRuntime(): boolean;
/**
 * Get the runtime extension
 * @returns {string}
 */
export function getRuntimeExtension(): string;
export function getRequire(callerPath: string): any;
export function getDirname(): any;
export function getDependency(dependencyName: string, callerPathOrUrl: string): string;
