<?php

declare(strict_types=1);

namespace utils\exception;

use Exception;

final class SingletonUnserializeException extends Exception
{
    public function __construct()
    {
        parent::__construct('Cannot unserialize a singleton');
    }
}
