export class ExceptionThrower {
    static throwException(commandException: any): Error;
    static serializeStack(stackTraceClasses: any, stackTraceMethods: any, stackTraceLines: any, stackTraceFiles: any): string;
}
