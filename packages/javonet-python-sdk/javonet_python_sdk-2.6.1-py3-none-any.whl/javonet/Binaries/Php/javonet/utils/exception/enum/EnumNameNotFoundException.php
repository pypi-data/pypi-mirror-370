<?php

declare(strict_types=1);

namespace utils\exception\enum;

use RuntimeException;

class EnumNameNotFoundException extends RuntimeException
{
    public function __construct(string $value)
    {
        parent::__construct('No matching constant name found for value: ' . $value);
    }
}
