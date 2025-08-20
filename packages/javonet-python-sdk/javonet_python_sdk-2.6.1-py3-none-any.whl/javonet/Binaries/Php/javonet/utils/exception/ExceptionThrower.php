<?php

declare(strict_types=1);

namespace utils\exception;

use ArithmeticError;
use DivisionByZeroError;
use InvalidArgumentException;
use OutOfBoundsException;
use RuntimeException;
use Throwable;
use TypeError;
use utils\Command;
use utils\messagehelper\MessageHelper;
use utils\type\ExceptionType;

final class ExceptionThrower
{
    public static function throwException(Command $commandException): void
    {
        try {
            $exceptionMessage = 'PHP Exception with empty message';
            $exceptionName = 'PHP Exception';
            $stackTrace = 'Javonet Exception with empty stack trace';
            $javonetStackCommand = 'Javonet Exception with empty stack command';
            $exceptionType = ExceptionType::EXCEPTION();

            switch ($commandException->getPayloadSize()) {
                case ExceptionType::DIVIDE_BY_ZERO_EXCEPTION:
                    $stackTrace = self::getLocalStackTrace($commandException->getPayload());
                case ExceptionType::ARITHMETIC_EXCEPTION:
                    $exceptionMessage = (string) ($commandException->getPayload()[3]);
                case ExceptionType::RUNTIME_EXCEPTION:
                    $exceptionName = (string) ($commandException->getPayload()[2]);
                case ExceptionType::FILE_NOT_FOUND_EXCEPTION:
                    $javonetStackCommand = (string) ($commandException->getPayload()[1]);
                case ExceptionType::IO_EXCEPTION:
                    $exceptionType = ExceptionType::from((int) ($commandException->getPayload()[0]));
                    break;
                default:
                    throw new RuntimeException('Error while processing exception: ' . $commandException);
            }

            $finalMessage = sprintf('[%s]: %s: %s: %s: %s', $exceptionName, $exceptionMessage, $stackTrace, $javonetStackCommand, $exceptionType->getName());

            switch ($exceptionType->getValue()) {
                case ExceptionType::EXCEPTION:
                case ExceptionType::RUNTIME_EXCEPTION:
                    throw new RuntimeException($finalMessage);
                case ExceptionType::IO_EXCEPTION:
                    throw new RuntimeException($finalMessage);
                case ExceptionType::ARITHMETIC_EXCEPTION:
                    throw new ArithmeticError($finalMessage);
                case ExceptionType::DIVIDE_BY_ZERO_EXCEPTION:
                    throw new DivisionByZeroError($finalMessage);
                case ExceptionType::NULL_POINTER_EXCEPTION:
                    throw new TypeError($finalMessage);
                case ExceptionType::FILE_NOT_FOUND_EXCEPTION:
                    throw new RuntimeException($finalMessage);
                case ExceptionType::ILLEGAL_ARGUMENT_EXCEPTION:
                    throw new InvalidArgumentException($finalMessage);
                case ExceptionType::INDEX_OUT_OF_BOUNDS_EXCEPTION:
                    throw new OutOfBoundsException($finalMessage);
                default:
                    throw new RuntimeException('Error while processing unknown exception type: ' . $commandException);
            }
        } catch (Throwable $e) {
            MessageHelper::getInstance()->sendMessageToAppInsights('SdkException: ', $e->getMessage());
            throw $e;
        }
    }

    private static function getLocalStackTrace(array $commandExceptionPayload): string
    {
        $stackClasses = self::splitIfNotEmpty($commandExceptionPayload[4]);
        $stackMethods = self::splitIfNotEmpty($commandExceptionPayload[5]);
        $stackLines = self::splitIfNotEmpty($commandExceptionPayload[6]);
        $stackFiles = self::splitIfNotEmpty($commandExceptionPayload[7]);

        $stackTrace = '';
        foreach ($stackClasses as $i => $class)
        {
            if (!empty($stackFiles[$i])) {
                $stackTrace .= sprintf('File "%s"', $stackFiles[$i]);
            }

            if (!empty($stackLines[$i])) {
                $stackTrace .= sprintf(', line %s', self::getStackLine($stackLines[$i]));
            }

            if (!empty($stackMethods[$i])) {
                $stackTrace .= sprintf(', in %s', $stackMethods[$i]);
            }

            $stackTrace .= "\n";
            if (!empty($class)) {
                $stackTrace .= sprintf("    %s\n", $class);
            }
        }

        return $stackTrace;
    }

    private static function splitIfNotEmpty(?string $input): array
    {
        return empty($input) ? [] : explode('|', $input);
    }

    private static function getStackLine($stackLine): int
    {
        if (is_numeric($stackLine)) {
            return (int) $stackLine;
        }

        return 0;
    }
}
