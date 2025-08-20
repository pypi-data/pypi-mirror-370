<?php

declare(strict_types=1);

namespace utils\type;

use utils\Enum;

final class ExceptionType extends Enum
{
    public const EXCEPTION = 0;
    public const IO_EXCEPTION = 1;
    public const FILE_NOT_FOUND_EXCEPTION = 2;
    public const RUNTIME_EXCEPTION = 3;
    public const ARITHMETIC_EXCEPTION = 4 ;
    public const ILLEGAL_ARGUMENT_EXCEPTION = 5;
    public const INDEX_OUT_OF_BOUNDS_EXCEPTION = 6;
    public const NULL_POINTER_EXCEPTION = 7;
    public const DIVIDE_BY_ZERO_EXCEPTION = 8;

    public static function getExceptionCodeByExceptionName(string $exceptionName): int
    {
        switch ($exceptionName) {
            case 'IOException':
                return self::IO_EXCEPTION;
            case 'FileNotFoundException':
                return self::FILE_NOT_FOUND_EXCEPTION;
            case 'RuntimeException':
                return self::RUNTIME_EXCEPTION;
            case 'ArithmeticError':
                return self::ARITHMETIC_EXCEPTION;
            case 'InvalidArgumentException':
                return self::ILLEGAL_ARGUMENT_EXCEPTION;
            case 'OutOfBoundsException':
            case 'OutOfRangeException':
                return self::INDEX_OUT_OF_BOUNDS_EXCEPTION;
            case 'TypeError':
                return self::NULL_POINTER_EXCEPTION;
            case 'DivisionByZeroError':
                return self::DIVIDE_BY_ZERO_EXCEPTION;
            default:
                return self::EXCEPTION;
        }
    }
}
