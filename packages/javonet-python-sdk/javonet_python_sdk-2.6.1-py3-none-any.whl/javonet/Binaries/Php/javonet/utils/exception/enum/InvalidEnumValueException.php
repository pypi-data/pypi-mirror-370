<?php

declare(strict_types=1);

namespace utils\exception\enum;

use RuntimeException;

final class InvalidEnumValueException extends RuntimeException
{
    public function __construct(string $className, int $value)
    {
        parent::__construct(sprintf('Invalid value: %d for class: %s', $value, $className));
    }
}
