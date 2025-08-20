<?php

declare(strict_types=1);

namespace utils\exception;

use RuntimeException;

final class JavonetArgumentsMismatchException extends RuntimeException
{
    public function __construct(string $commandName, int $requiredArgumentsCount)
    {
        parent::__construct('Wrong argument number for command: '
            . $commandName . ' minimal required for this command is: '
            . $requiredArgumentsCount);
    }
}
