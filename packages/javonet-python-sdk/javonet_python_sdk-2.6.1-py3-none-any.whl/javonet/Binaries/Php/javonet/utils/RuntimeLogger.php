<?php

declare(strict_types=1);

namespace utils;

use Exception;

final class RuntimeLogger {
    private static bool $notLoggedYet = true;

    public static function getRuntimeInfo(): string
    {
        try {
            return sprintf(
                "PHP Managed Runtime Info:\n" .
                "PHP Version: %s\n" .
                "PHP executable path: %s\n" .
                "PHP Path: %s\n" .
                "PHP Implementation: %s\n" .
                "OS Version: %s %s\n" .
                "Process Architecture: %s\n" .
                "Current Working Directory: %s\n",
                PHP_VERSION,
                PHP_BINARY,
                get_include_path(),
                PHP_SAPI,
                PHP_OS_FAMILY,
                php_uname('r'),
                php_uname('m'),
                getcwd()
            );
        } catch (Exception $e) {
            return 'PHP Managed Runtime Info: Error while fetching runtime info';
        }
    }

    public static function displayRuntimeInfo(): void
    {
        if (self::$notLoggedYet) {
            echo self::getRuntimeInfo();
            self::$notLoggedYet = false;
        }
    }
}