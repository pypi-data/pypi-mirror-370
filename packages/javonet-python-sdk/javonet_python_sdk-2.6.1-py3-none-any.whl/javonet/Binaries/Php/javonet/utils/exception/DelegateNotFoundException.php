<?php

declare(strict_types=1);

namespace utils\exception;

use InvalidArgumentException;

final class DelegateNotFoundException extends InvalidArgumentException
{
    public function __construct(string $delegateId)
    {
        parent::__construct('Delegate not found for ID: ' . $delegateId);
    }
}