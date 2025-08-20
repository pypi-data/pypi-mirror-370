<?php

declare(strict_types=1);

namespace utils\exception;

use RuntimeException;

final class TypeNotSupportedException extends RuntimeException
{
    public function __construct(string $typeName)
    {
        parent::__construct(
            'Unsupported Reflection Type conversion for Javonet type : ' . $typeName
        );
    }
}