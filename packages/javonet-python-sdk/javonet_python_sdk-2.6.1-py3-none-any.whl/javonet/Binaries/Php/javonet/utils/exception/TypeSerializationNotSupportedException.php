<?php

declare(strict_types=1);

namespace utils\exception;

use RuntimeException;

class TypeSerializationNotSupportedException extends RuntimeException
{
    public function __construct($typeSerialization)
    {
        parent::__construct(
            sprintf('PHP: Type serialization not supported for type: %s' ,
                is_object($typeSerialization) ? get_class($typeSerialization) : gettype($typeSerialization)
            )
        );
    }
}