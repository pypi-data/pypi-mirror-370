export class ExceptionSerializer {
    static serializeException(exception: any, command: any): Command;
    static getExceptionCode(exception: any): 0 | 5 | 6;
    static serializeStackTrace(exception: any, stackClasses: any, stackMethods: any, stackLines: any, stackFiles: any): void;
}
import { Command } from '../Command.js';
