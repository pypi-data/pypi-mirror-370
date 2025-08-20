<?php

declare(strict_types=1);

namespace utils\exception;

use RuntimeException;

class BadMethodCallException extends RuntimeException
{
    public function __construct(string $staticClass, string $method)
    {
        parent::__construct(sprintf('Method %s does not exist in %s', $method, $staticClass));
    }
}