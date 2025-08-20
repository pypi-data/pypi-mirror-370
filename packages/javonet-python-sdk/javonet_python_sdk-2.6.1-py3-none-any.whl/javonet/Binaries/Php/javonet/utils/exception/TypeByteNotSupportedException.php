<?php

declare(strict_types=1);

namespace utils\exception;

use RuntimeException;

final class TypeByteNotSupportedException extends RuntimeException
{
    public function __construct(int $typeNum)
    {
        parent::__construct(sprintf('Type byte value: %d not supported', $typeNum));
    }
}