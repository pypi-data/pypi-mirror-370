<?php

declare(strict_types=1);

namespace utils;

final class StringEncodingMode extends Enum
{
    public const JAVONET_ASCII = 0;
    public const JAVONET_UTF8 = 1;
    public const JAVONET_UTF16 = 2;
    public const JAVONET_UTF32 = 3;
}