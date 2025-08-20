<?php

declare(strict_types=1);

namespace utils;

final class RuntimeName extends Enum
{
    public const CLR = 0;
    public const GO = 1;
    public const JVM = 2;
    public const NETCORE = 3;
    public const PERL = 4;
    public const PYTHON = 5;
    public const RUBY = 6;
    public const NODEJS = 7;
    public const CPP = 8;
    public const PHP = 9;
    public const PYTHON27 = 10;
    public const NONE = 11;
}
