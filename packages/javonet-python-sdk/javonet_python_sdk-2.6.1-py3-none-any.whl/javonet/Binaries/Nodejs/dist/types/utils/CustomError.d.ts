export class CustomError extends Error {
    /**
     * @param {string} message
     * @param {string} cause
     */
    constructor(message: string, cause: string);
}
