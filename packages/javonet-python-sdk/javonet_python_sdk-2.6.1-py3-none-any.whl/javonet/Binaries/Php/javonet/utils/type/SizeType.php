<?php

declare(strict_types=1);

namespace utils\type;

use utils\Enum;

final class SizeType extends Enum
{
    public const JAVONET_BOOLEAN_SIZE = 1;
    public const JAVONET_BYTE_SIZE = 1;
    public const JAVONET_CHAR_SIZE = 1;
    public const JAVONET_INTEGER_SIZE = 4;
    public const JAVONET_FLOAT_SIZE = 4;
    public const JAVONET_LONG_SIZE = 8;
    public const JAVONET_DOUBLE_SIZE = 8;
    public const JAVONET_UNSIGNED_LONG_LONG_SIZE = 8;
    public const JAVONET_UNSIGNED_INTEGER_SIZE  = 4;
    public const JAVONET_NULL_SIZE = 1;
}