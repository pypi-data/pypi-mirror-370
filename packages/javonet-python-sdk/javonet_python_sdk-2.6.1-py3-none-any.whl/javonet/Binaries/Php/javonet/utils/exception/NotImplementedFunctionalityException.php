<?php

declare(strict_types=1);

namespace utils\exception;

use Exception;

final class NotImplementedFunctionalityException extends Exception
{
    public function __construct()
    {
        parent::__construct('Not implemented functionality');
    }
}
