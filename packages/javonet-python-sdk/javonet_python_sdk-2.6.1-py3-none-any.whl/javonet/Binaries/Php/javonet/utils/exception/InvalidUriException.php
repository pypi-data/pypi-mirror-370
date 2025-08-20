<?php

declare(strict_types=1);

namespace utils\exception;

use InvalidArgumentException;

final class InvalidUriException extends InvalidArgumentException
{
    public function __construct(string $uri)
    {
        parent::__construct('Invalid URI: ' . $uri);
    }
}