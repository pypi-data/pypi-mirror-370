<?php

declare(strict_types=1);

namespace utils\type;

use utils\Enum;

final class JType extends Enum
{
    public const JAVONET_COMMAND = 0;
    public const JAVONET_STRING = 1;
    public const JAVONET_INTEGER = 2;
    public const JAVONET_BOOLEAN = 3;
    public const JAVONET_FLOAT = 4;
    public const JAVONET_BYTE = 5;
    public const JAVONET_CHAR = 6;
    public const JAVONET_LONG = 7;
    public const JAVONET_DOUBLE = 8;
    public const JAVONET_UNSIGNED_LONG_LONG = 9;
    public const JAVONET_UNSIGNED_INTEGER = 10;
    public const JAVONET_NULL = 11;
    public const JAVONET_VOID = 12;
}